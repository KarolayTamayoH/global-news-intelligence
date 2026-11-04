"""Contract tests use synthetic ZIPs and the actual DAG task bodies.

Airflow scheduling/import is a separate deployment check; it is not simulated here.
"""
import ast
import csv
import io
import logging
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.validation.validate_gkg import (
    EXPECTED_COLUMNS, validate_gkg, validate_gkg_archive, validate_target_date,
)

ROOT = Path(__file__).resolve().parents[1]


def make_zip(rows=None, header=None, member='20261027.gkg.csv'):
    content = io.StringIO(newline='')
    writer = csv.writer(content, delimiter='\t')
    writer.writerow(EXPECTED_COLUMNS if header is None else header)
    writer.writerows([['20261027', '1'] + [''] * 9] if rows is None else rows)
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr(member, content.getvalue())
    return output.getvalue()


def task_body(name, **namespace):
    """Load only a task's Python body without requiring an Airflow installation."""
    tree = ast.parse((ROOT / 'dags/global_news_ingestion.py').read_text())
    function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    function.decorator_list = []
    module = ast.Module(body=[function], type_ignores=[])
    exec(compile(module, 'dags/global_news_ingestion.py', 'exec'), namespace)
    return namespace[name]


class ValidationTests(unittest.TestCase):
    def test_path_stream_and_dag_agree_and_skip_header(self):
        payload = make_zip(rows=[['20261027', '1'] + [''] * 9] * 2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '20261027.gkg.csv.zip'
            path.write_bytes(payload)
            local = validate_gkg(path)
        stream = validate_gkg_archive(io.BytesIO(payload), '20261027')
        task = task_body('download_and_validate', io=io, logging=logging,
                         validate_gkg_archive=validate_gkg_archive,
                         urlopen=lambda *a, **kw: io.BytesIO(payload))
        result = task({'url': 'https://example.invalid/fixture', 'date': '20261027'})
        self.assertEqual(local, {'total': 2, 'invalid': 0})
        self.assertEqual(local, stream)
        self.assertEqual(result['records'], local['total'])

    def test_invalid_archives_rejected_locally_and_in_task(self):
        cases = {
            'header': make_zip(header=['wrong'] * 11),
            'empty': make_zip(rows=[]),
            'columns': make_zip(rows=[['20261027', '1']]),
            'different date': make_zip(rows=[['20261026', '1'] + [''] * 9]),
            'invalid timestamp': make_zip(rows=[['20261027250000', '1'] + [''] * 9]),
            'invalid articles': make_zip(rows=[['20261027', '-1'] + [''] * 9]),
            'non-ascii articles': make_zip(rows=[['20261027', '²'] + [''] * 9]),
            'wrong member': make_zip(member='other.csv'),
            'corrupt': b'not a ZIP',
        }
        # Damage the stored CSV bytes while preserving the ZIP directory.
        corrupt_crc = bytearray(make_zip())
        position = corrupt_crc.index(b'DATE')
        corrupt_crc[position] = ord('X')
        cases['CRC mismatch'] = bytes(corrupt_crc)
        for name, payload in cases.items():
            with self.subTest(name=name):
                task = task_body('download_and_validate', io=io, logging=logging,
                                 validate_gkg_archive=validate_gkg_archive,
                                 urlopen=lambda *a, **kw: io.BytesIO(payload))
                with self.assertRaises((ValueError, zipfile.BadZipFile)):
                    validate_gkg_archive(io.BytesIO(payload), '20261027')
                with self.assertRaises((ValueError, zipfile.BadZipFile)):
                    task({'url': 'https://example.invalid/fixture', 'date': '20261027'})

    def test_calendar_dates_are_strict(self):
        for date in ['20260230', '20261301', '2026113', '2026-11-03', '', None, 20261103]:
            with self.subTest(date=date), self.assertRaises(ValueError):
                validate_target_date(date)
        self.assertEqual(validate_target_date('20240229'), '20240229')

    def test_manual_partition_does_not_depend_on_current_clock(self):
        task = task_body('check_availability', validate_target_date=validate_target_date,
                         GDELT_BASE_URL='https://example.invalid', logging=logging,
                         urlopen=lambda *a, **kw: io.BytesIO(b'ZIP'))
        result = task(dag_run=SimpleNamespace(conf={'target_date': '20261027'}))
        self.assertEqual(result['date'], '20261027')
        with self.assertRaisesRegex(ValueError, 'fecha logica'):
            task(dag_run=SimpleNamespace(conf={}))

    def test_retries_keep_the_same_logical_partition(self):
        logical_date = MagicMock()
        logical_date.in_timezone.return_value.subtract.return_value.format.return_value = '20261027'
        task = task_body('check_availability', validate_target_date=validate_target_date,
                         GDELT_BASE_URL='https://example.invalid', logging=logging,
                         urlopen=lambda *a, **kw: io.BytesIO(b'ZIP'))
        context = {'dag_run': SimpleNamespace(conf={}), 'logical_date': logical_date}
        self.assertEqual(task(**context)['date'], '20261027')
        self.assertEqual(task(**context)['date'], '20261027')
        logical_date.in_timezone.assert_called_with('UTC')
        logical_date.in_timezone.return_value.subtract.assert_called_with(days=1)


if __name__ == '__main__':
    unittest.main()
