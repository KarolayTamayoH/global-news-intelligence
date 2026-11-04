"""Contratos de validacion local y etapas compartidas por el DAG, con ZIPs sinteticos."""
import csv
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from src.validation.validate_gkg import (
    EXPECTED_COLUMNS, validate_gkg, validate_gkg_archive, validate_target_date,
)

from src.pipeline.artifacts import ArtifactStore
from src.pipeline.tasks import validate_partition, select_partition
from datetime import datetime, timezone


def make_zip(rows=None, header=None, member='20261027.gkg.csv'):
    content = io.StringIO(newline='')
    writer = csv.writer(content, delimiter='\t')
    writer.writerow(EXPECTED_COLUMNS if header is None else header)
    writer.writerows([['20261027', '1'] + [''] * 9] if rows is None else rows)
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr(member, content.getvalue())
    return output.getvalue()




class ValidationTests(unittest.TestCase):
    def test_path_stream_and_dag_agree_and_skip_header(self):
        payload = make_zip(rows=[['20261027', '1'] + [''] * 9] * 2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '20261027.gkg.csv.zip'
            path.write_bytes(payload)
            local = validate_gkg(path)
        stream = validate_gkg_archive(io.BytesIO(payload), '20261027')
        with tempfile.TemporaryDirectory() as directory:
            store = ArtifactStore(Path(directory).as_uri())
            path = Path(directory) / 'source.zip'
            path.write_bytes(payload)
            uri = store.publish(path, 'raw/20261027.gkg.csv.zip')
            with patch('src.pipeline.tasks.ArtifactStore', return_value=store), \
                 patch('src.pipeline.tasks.update_history'):
                result = validate_partition({'date': '20261027', 'run_id': 'test', 'raw_uri': uri})
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
                with self.assertRaises((ValueError, zipfile.BadZipFile)):
                    validate_gkg_archive(io.BytesIO(payload), '20261027')
                with tempfile.TemporaryDirectory() as directory:
                    store = ArtifactStore(Path(directory).as_uri())
                    path = Path(directory) / 'source.zip'
                    path.write_bytes(payload)
                    uri = store.publish(path, 'raw/20261027.gkg.csv.zip')
                    with patch('src.pipeline.tasks.ArtifactStore', return_value=store), \
                         patch('src.pipeline.tasks.update_history'), \
                         self.assertRaises((ValueError, zipfile.BadZipFile)):
                        validate_partition({'date': '20261027', 'run_id': 'test', 'raw_uri': uri})

    def test_calendar_dates_are_strict(self):
        for date in ['20260230', '20261301', '2026113', '2026-11-03', '', None, 20261103]:
            with self.subTest(date=date), self.assertRaises(ValueError):
                validate_target_date(date)
        self.assertEqual(validate_target_date('20240229'), '20240229')

    def test_manual_partition_does_not_depend_on_current_clock(self):
        result = select_partition({'target_date': '20261027'}, None, 'manual-test')
        self.assertEqual(result['date'], '20261027')
        with self.assertRaisesRegex(ValueError, 'intervalo'):
            select_partition({}, None, 'manual-test')

    def test_retries_keep_the_same_partition_from_interval_end(self):
        end = datetime(2026, 10, 28, 6, tzinfo=timezone.utc)
        first = select_partition({}, end, 'scheduled-test')
        self.assertEqual(first['date'], '20261027')
        self.assertEqual(first, select_partition({}, end, 'scheduled-test'))
        self.assertNotEqual(first['prefix'], select_partition({}, end, 'another-run')['prefix'])


if __name__ == '__main__':
    unittest.main()
