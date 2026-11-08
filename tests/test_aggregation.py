from collections import Counter
from datetime import date
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.transformation import aggregate_snapshot as aggregation


class Result(list):
    def one(self):
        return self[0] if self else None


class MemorySession:
    """Modelo de almacenamiento que conserva generaciones entre intentos."""
    def __init__(self):
        self.current = uuid4()
        self.values = {}
        self.publications = 0

    def prepare(self, query):
        return SimpleNamespace(query=query)

    def execute(self, statement, params=None):
        query = statement if isinstance(statement, str) else statement.query
        if query.startswith('INSERT INTO daily_news_metrics'):
            self.current = params[-1]
            self.publications += 1
        elif query.startswith('INSERT INTO'):
            table = query.split()[2]
            day, generation, entity, count = params
            self.values.setdefault((table, day, generation), {})[entity] = count
        elif 'SELECT generation' in query:
            return Result([SimpleNamespace(generation=self.current)])
        else:
            field = query.split()[1].rstrip(',')
            table = query.split('FROM ')[1].split()[0]
            return Result(SimpleNamespace(**{field: entity, 'record_count': count})
                          for entity, count in self.values.get((table, *params), {}).items())


def execute_rows(session, statement, parameters, **kwargs):
    for values in parameters:
        session.execute(statement, values)
    return []


class AggregationTests(unittest.TestCase):
    def snapshot(self):
        return aggregation.calculate_snapshot([
            {'themes': [' A ', 'A', 'B'], 'organizations': ['Org'], 'tone_raw': '-2,0'},
            {'themes': ['B'], 'organizations': ['Org', 'Other'], 'tone_raw': '4,0'},
        ])

    def test_deduplicates_entities_and_excludes_nonfinite_tones(self):
        result = aggregation.calculate_snapshot([
            {'themes': [' A ', 'A', '', None], 'tone_raw': 'nan'},
            {'themes': ['A'], 'tone_raw': 'inf'},
            {'tone_raw': '-2,0'}, {'tone_raw': None},
        ])
        self.assertEqual(result['themes'], Counter(A=2))
        self.assertEqual(result['total_records'], 4)
        self.assertEqual(result['average_tone'], -2)

    def test_empty_partition_performs_no_cassandra_writes(self):
        mongo, cluster = MagicMock(), MagicMock()
        mongo.__enter__.return_value.__getitem__.return_value.__getitem__.return_value.find.return_value = []
        with patch.object(aggregation, 'MongoClient', return_value=mongo), \
             patch.object(aggregation, 'Cluster', return_value=cluster):
            with self.assertRaisesRegex(ValueError, 'No hay registros'):
                aggregation.aggregate_snapshot('20261027')
        cluster.connect.return_value.execute.assert_not_called()
        cluster.shutdown.assert_called_once()

    def test_partial_failure_preserves_visible_generation_and_retry_replaces_it(self):
        session = MemorySession()
        old = session.current
        attempts = 0

        def fail_on_organizations(session, statement, parameters, **kwargs):
            nonlocal attempts
            attempts += 1
            execute_rows(session, statement, parameters)
            if attempts == 2:
                raise RuntimeError('interrupted')
            return []

        with patch.object(aggregation, 'execute_concurrent_with_args', side_effect=fail_on_organizations):
            with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                aggregation.publish_snapshot(session, date(2026, 10, 27), self.snapshot())
        self.assertEqual(session.current, old)
        self.assertEqual(session.publications, 0)
        failed_versions = {key[2] for key in session.values}
        with patch.object(aggregation, 'execute_concurrent_with_args', side_effect=execute_rows):
            new = aggregation.publish_snapshot(session, date(2026, 10, 27), self.snapshot())
        self.assertNotIn(new, failed_versions)
        self.assertEqual(session.current, new)
        self.assertEqual(session.publications, 1)
        self.assertEqual({r.theme: r.record_count for r in aggregation.active_entity_metrics(
            session, date(2026, 10, 27), 'theme')}, {'A': 1, 'B': 2})

    def test_missing_write_is_detected_before_publication(self):
        session = MemorySession()
        old = session.current
        with patch.object(aggregation, 'execute_concurrent_with_args', return_value=[]):
            with self.assertRaisesRegex(ValueError, 'Version incompleta'):
                aggregation.publish_snapshot(session, date(2026, 10, 27), self.snapshot())
        self.assertEqual(session.current, old)
        self.assertEqual(session.publications, 0)

    def test_empty_entity_lists_can_publish_without_old_entities(self):
        session = MemorySession()
        snapshot = aggregation.calculate_snapshot([{'themes': [], 'organizations': []}])
        with patch.object(aggregation, 'execute_concurrent_with_args', side_effect=execute_rows):
            aggregation.publish_snapshot(session, date(2026, 10, 27), snapshot)
        self.assertEqual(list(aggregation.active_entity_metrics(
            session, date(2026, 10, 27), 'theme')), [])
        self.assertEqual(session.publications, 1)

    def test_recalculation_hides_removed_entities_and_preserves_existing_readers(self):
        session = MemorySession()
        day = date(2026, 10, 27)
        with patch.object(aggregation, 'execute_concurrent_with_args', side_effect=execute_rows):
            old = aggregation.publish_snapshot(session, day, self.snapshot())
            changed = aggregation.calculate_snapshot([{'themes': ['C']}])
            aggregation.publish_snapshot(session, day, changed)
        self.assertEqual({r.theme for r in aggregation.active_entity_metrics(
            session, day, 'theme')}, {'C'})
        self.assertEqual({r.theme for r in aggregation.read_entity_metrics(
            session, day, 'theme', old)}, {'A', 'B'})
        self.assertEqual(list(aggregation.active_entity_metrics(session, day, 'organization')), [])


if __name__ == '__main__':
    unittest.main()
