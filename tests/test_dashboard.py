import unittest
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

    def run_dashboard(self, with_themes):
        daily = [SimpleNamespace(
            news_date=SimpleNamespace(date=lambda d=d: date(2026, 10, d)),
            total_records=count, unique_themes=2, average_tone=None,
        ) for d, count in [(26, 0), (27, 2)]]

        class Session:
            def execute(self, query, params=None):
                if 'daily_news_metrics' in query:
                    return daily
                if 'daily_theme_metrics' in query:
                    return [SimpleNamespace(theme='EPU_POLICY', record_count=1)] if with_themes else []
                return [SimpleNamespace(organization='demo', record_count=1)]

        with patch('cassandra.cluster.Cluster') as cluster:
            cluster.return_value.connect.return_value = Session()
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'dashboard/app.py'))
            app.run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            app.selectbox[0].select(date(2026, 10, 26)).run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            return app

    def test_missing_themes_preserve_other_views_and_null_tone(self):
        app = self.run_dashboard(with_themes=False)
        titles = [item.value for item in app.subheader]
        self.assertIn('Diversidad tematica y tono informativo', titles)
        self.assertIn('Top 10 entidades organizacionales', titles)
        self.assertEqual(len(app.dataframe), 1)
        metrics = {item.label: item.value for item in app.metric}
        self.assertEqual(metrics['Tono promedio del ultimo dia'], 'N/D')
        self.assertEqual(metrics['Variacion diaria'], 'N/D')

    def test_theme_caption_matches_selected_date(self):
        app = self.run_dashboard(with_themes=True)
        captions = [item.value for item in app.caption]
        self.assertIn('Fecha analizada: 2026-10-26 | Un registro puede contener varios temas.', captions)


if __name__ == '__main__':
    unittest.main()
