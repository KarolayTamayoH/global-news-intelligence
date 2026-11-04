import unittest
from unittest.mock import MagicMock, patch

from src.transformation import aggregate_daily, aggregate_entities


class AggregationTests(unittest.TestCase):
    def test_empty_explicit_partition_does_not_replace_metrics(self):
        for module, function in [(aggregate_daily, aggregate_daily.aggregate_daily),
                                 (aggregate_entities, aggregate_entities.aggregate_entities)]:
            with self.subTest(module=module.__name__):
                mongo, cluster = MagicMock(), MagicMock()
                mongo.__getitem__.return_value.__getitem__.return_value.count_documents.return_value = 0
                session = cluster.connect.return_value
                with patch.object(module, 'MongoClient', return_value=mongo), \
                     patch.object(module, 'Cluster', return_value=cluster):
                    with self.assertRaisesRegex(ValueError, 'No hay registros'):
                        function('20261027')
                session.execute.assert_not_called()
                cluster.shutdown.assert_called_once()
                mongo.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
