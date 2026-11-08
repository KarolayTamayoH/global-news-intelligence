import unittest
from contextlib import ExitStack
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest


class DashboardTests(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()
        st.cache_resource.clear()

    def run_dashboard(self, with_themes=True, cassandra_failure=False, mongo_failure=False):
        daily = [SimpleNamespace(
            news_date=SimpleNamespace(date=lambda d=d: date(2026, 10, d)),
            total_records=count, unique_themes=2, average_tone=None, generation=None,
        ) for d, count in [(26, 0), (27, 2)]]

        class Result(list):
            def one(self):
                return self[0] if self else None

        class Session:
            def execute(self, query, params=None):
                if cassandra_failure:
                    raise RuntimeError('offline')
                if 'daily_news_metrics' in query:
                    return Result(daily)
                if 'daily_theme_metrics' in query:
                    return [SimpleNamespace(theme='EPU_POLICY', record_count=1)] if with_themes else []
                return [SimpleNamespace(organization='demo', record_count=1)]

        with ExitStack() as stack:
            cluster = stack.enter_context(patch('cassandra.cluster.Cluster'))
            cluster.return_value.connect.return_value = Session()
            stack.enter_context(patch('pymongo.MongoClient'))
            stack.enter_context(patch('neo4j.GraphDatabase.driver'))
            stack.enter_context(patch('src.config.NEO4J_PASSWORD', 'test-only'))
            stack.enter_context(patch('dashboard.queries.get_document_dates', return_value=[date(2026, 10, 26), date(2026, 10, 27)]))
            search = stack.enter_context(patch('dashboard.queries.search_documents', return_value={
                'total': 1, 'documents': [{'_id': 'record-1', 'num_articles': 1,
                                          'themes': ['EPU_POLICY'], 'organizations': ['demo']}]}))
            if mongo_failure:
                search.side_effect = RuntimeError('offline')
            stack.enter_context(patch('dashboard.queries.get_graph_counts', return_value={
                'records': 2, 'themes': 2, 'organizations': 1}))
            sample = stack.enter_context(patch('dashboard.queries.get_graph_sample', return_value=[{
                'record_id': 'record-1', 'entity_type': 'Theme', 'entity_name': 'EPU_POLICY',
                'relationship': 'HAS_THEME'}]))
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'dashboard/app.py'))
            app.run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            app.selectbox(key='analysis_date').select(date(2026, 10, 26)).run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(sample.call_args.args[1], '20261026')
            if not mongo_failure:
                self.assertEqual(search.call_args.args[1], '20261026')
            return app

    def test_missing_themes_preserve_other_views_and_null_tone(self):
        app = self.run_dashboard(with_themes=False)
        titles = [item.value for item in app.subheader]
        self.assertIn('Diversidad tematica y tono informativo', titles)
        self.assertIn('Top 10 entidades organizacionales', titles)
        self.assertIn('Explorador documental', titles)
        self.assertIn('Explorador de relaciones', titles)
        self.assertEqual(len(app.tabs), 3)
        metrics = {item.label: item.value for item in app.metric}
        self.assertEqual(metrics['Tono promedio del ultimo dia'], 'N/D')
        self.assertEqual(metrics['Variacion diaria'], 'N/D')

    def test_theme_caption_matches_selected_date(self):
        app = self.run_dashboard()
        self.assertIn('Fecha analizada: 2026-10-26 | Un registro puede contener varios temas.',
                      [item.value for item in app.caption])

    def test_cassandra_failure_preserves_mongo_and_neo4j_views(self):
        app = self.run_dashboard(cassandra_failure=True)
        metrics = {item.label: item.value for item in app.metric}
        self.assertEqual(metrics['Registros encontrados en MongoDB'], '1')
        self.assertEqual(metrics['Registros en Neo4j'], '2')
        self.assertTrue(any('Cassandra no está disponible' in item.value for item in app.warning))

    def test_mongodb_failure_preserves_graph(self):
        app = self.run_dashboard(mongo_failure=True)
        self.assertTrue(any('documentos de MongoDB' in item.value for item in app.warning))
        self.assertIn('Registros en Neo4j', [item.label for item in app.metric])


if __name__ == '__main__':
    unittest.main()
