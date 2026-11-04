import unittest
from unittest.mock import MagicMock

from dashboard.queries import search_documents, get_graph_sample
from dashboard.graph import graph_figure
from src.config import MONGO_DATABASE


class DashboardQueryTests(unittest.TestCase):
    def test_document_filter_is_literal_and_pagination_bounded(self):
        client = MagicMock()
        collection = client[MONGO_DATABASE]['gkg_records']
        collection.count_documents.return_value = 42
        cursor = collection.find.return_value.sort.return_value.skip.return_value.limit.return_value
        cursor.__iter__.return_value = iter([{'_id': 'id-1'}])
        result = search_documents(client, '20261027', 'EPU_POLICY', 'a.*b', page=2, page_size=20)
        query = collection.find.call_args.args[0]
        self.assertEqual(query['organizations']['$regex'], r'a\.\*b')
        self.assertEqual(query['date'], '20261027')
        collection.find.return_value.sort.return_value.skip.assert_called_once_with(20)
        collection.find.return_value.sort.return_value.skip.return_value.limit.assert_called_once_with(20)
        self.assertEqual(result['total'], 42)
        with self.assertRaises(ValueError):
            search_documents(client, '20261027', page_size=101)

    def test_graph_text_is_parameterized_and_limit_applies_before_expansion(self):
        driver = MagicMock()
        text = "' MATCH (n) DETACH DELETE n //"
        get_graph_sample(driver, '20261027', 'Theme', text, 3)
        call = driver.session.return_value.__enter__.return_value.run.call_args
        query = call.args[0]
        self.assertNotIn(text, query)
        self.assertEqual(call.kwargs['entity_name'], text)
        self.assertLess(query.index('LIMIT $record_limit'), query.index('OPTIONAL MATCH'))
        with self.assertRaises(ValueError):
            get_graph_sample(driver, '20261027', 'ArbitraryLabel', '', 3)

    def test_graph_preserves_records_without_entities(self):
        figure = graph_figure([{'record_id': 'sample-record', 'entity_type': None,
                                'entity_name': None, 'relationship': None}])
        self.assertEqual(figure.data[-1].name, 'Registros GKG')
        self.assertEqual(list(figure.data[-1].customdata), ['sample-record'])


if __name__ == '__main__':
    unittest.main()
