import unittest
from unittest.mock import MagicMock, patch

from src.ingestion import load_neo4j as loader


class Neo4jLoadingTests(unittest.TestCase):
    def run_load(self, expected, stored, previous=None):
        mongo = MagicMock()
        database = mongo.__getitem__.return_value
        collection = MagicMock()
        history = MagicMock()
        database.__getitem__.side_effect = lambda name: (
            collection if name == 'gkg_records' else history)
        history.find_one.return_value = previous
        documents = [{'_id': str(i), 'date': '20261027'} for i in range(expected)]
        collection.find.return_value.sort.return_value = documents
        collection.count_documents.return_value = expected
        driver = MagicMock()
        session = driver.session.return_value.__enter__.return_value
        session.run.return_value.single.return_value = {'total': stored}
        with patch.object(loader, 'NEO4J_PASSWORD', 'test-only'), \
             patch.object(loader, 'MongoClient', return_value=mongo), \
             patch.object(loader.GraphDatabase, 'driver', return_value=driver):
            try:
                loader.load_neo4j('20261027')
            finally:
                self.history = history
                self.session = session
                mongo.close.assert_called_once()
                driver.close.assert_called_once()

    def test_matching_nonempty_graph_is_checked_before_completed(self):
        self.run_load(expected=2, stored=2)
        self.session.run.assert_called_once()
        self.history.update_one.assert_called_once()

    def test_mismatch_does_not_mark_completed(self):
        with self.assertRaisesRegex(ValueError, 'Neo4j contiene 1'):
            self.run_load(expected=2, stored=1)
        self.history.update_one.assert_not_called()

    def test_empty_partition_does_not_mark_completed(self):
        with self.assertRaisesRegex(ValueError, 'No hay registros'):
            self.run_load(expected=0, stored=0)
        self.history.update_one.assert_not_called()


if __name__ == '__main__':
    unittest.main()
