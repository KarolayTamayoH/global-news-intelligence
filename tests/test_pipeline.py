import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.pipeline.artifacts import ArtifactStore
from src.pipeline import tasks


class PipelineTests(unittest.TestCase):
    def test_persisted_artifact_can_be_read_by_another_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'input.zip'
            source.write_bytes(b'fixture')
            first = ArtifactStore((root / 'shared').as_uri())
            uri = first.publish(source, 'run/raw/20261027.gkg.csv.zip')
            source.unlink()
            second = ArtifactStore((root / 'shared').as_uri())
            output = second.fetch(uri, root / 'worker2/download.zip')
            self.assertEqual(output.read_bytes(), b'fixture')
            self.assertEqual(list((root / 'shared').rglob('*.part')), [])
            for key in ['../escape', 'run/../../escape', '/absolute', 'run//empty',
                        'run/%2e%2e/escape', 'run/file?query']:
                with self.subTest(key=key), self.assertRaises(ValueError):
                    first.uri(key)
            with self.assertRaises(ValueError):
                second.fetch('file:///other/storage.zip', root / 'outside.zip')

    def test_storage_requires_an_absolute_local_file_uri(self):
        for uri in ['https://example.invalid/data', 'file://remote/data',
                    'relative/data', 'file:///tmp/data?query=1']:
            with self.subTest(uri=uri), self.assertRaises(ValueError):
                ArtifactStore(uri)

    def test_artifact_storage_handles_project_paths_with_spaces(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'big data'
            root.mkdir()
            source = root / 'source.jsonl'
            source.write_text('{"date":"20261027"}\n')
            store = ArtifactStore((root / 'shared artifacts').as_uri())
            uri = store.publish(source, 'run/processed/20261027.jsonl')
            output = store.fetch(uri, root / 'another worker/20261027.jsonl')
            self.assertIn('%20', uri)
            self.assertEqual(output.read_text(), source.read_text())

    def test_failed_reconciliation_cannot_publish_or_complete_run(self):
        info = {'date': '20261027', 'run_id': 'test', 'records': 2, 'prefix': 'runs/test'}
        with patch('scripts.verify_partition.verify_partition', side_effect=ValueError('mismatch')), \
             patch.object(tasks, 'update_history') as history, \
             patch.object(ArtifactStore, 'publish') as publish:
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                tasks.finalize_partition(info)
        publish.assert_not_called()
        statuses = [call.args[1].get('status') for call in history.call_args_list]
        self.assertIn('failed', statuses)
        self.assertNotIn('completed', statuses)

    def test_transformation_checks_record_count_before_publish(self):
        from test_validation import make_zip
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / '20261027.gkg.csv.zip'
            source.write_bytes(make_zip())
            store = ArtifactStore((root / 'shared').as_uri())
            uri = store.publish(source, 'raw/20261027.gkg.csv.zip')
            info = {'date': '20261027', 'run_id': 'test', 'records': 2,
                    'prefix': 'runs/test', 'raw_uri': uri}
            with patch.object(tasks, 'ArtifactStore', return_value=store), \
                 patch.object(tasks, 'update_history'), \
                 self.assertRaisesRegex(ValueError, 'conteo validado'):
                tasks.transform_partition(info)
            self.assertFalse((root / 'shared/runs/test/processed').exists())


if __name__ == '__main__':
    unittest.main()
