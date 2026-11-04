import importlib.util
import os
import unittest
from unittest.mock import patch

from src import config


class ConfigurationTests(unittest.TestCase):
    def load_config(self, values):
        spec = importlib.util.spec_from_file_location('isolated_config', config.__file__)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(os.environ, values, clear=True):
            spec.loader.exec_module(module)
        return module

    def test_remote_connections_and_data_root_can_be_overridden(self):
        settings = self.load_config({
            'MONGO_URI': 'mongodb://mongo.internal:27017/',
            'MONGO_DATABASE': 'demo',
            'CASSANDRA_HOST': 'cassandra.internal', 'CASSANDRA_PORT': '9042',
            'CASSANDRA_KEYSPACE': 'demo_analytics',
            'NEO4J_URI': 'bolt://graph.internal:7687',
            'GNI_DATA_DIR': 'data-fixture',
        })
        self.assertEqual(settings.MONGO_URI, 'mongodb://mongo.internal:27017/')
        self.assertEqual(settings.CASSANDRA_PORT, 9042)
        self.assertEqual(settings.CASSANDRA_KEYSPACE, 'demo_analytics')
        self.assertEqual(settings.NEO4J_URI, 'bolt://graph.internal:7687')
        self.assertEqual(settings.PROCESSED_DIR, config.ROOT / 'data-fixture/processed')

    def test_invalid_port_or_keyspace_fails_before_connecting(self):
        for values in [{'CASSANDRA_PORT': '0'}, {'CASSANDRA_PORT': '70000'},
                       {'CASSANDRA_KEYSPACE': 'bad; DROP KEYSPACE other'}]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.load_config(values)


if __name__ == '__main__':
    unittest.main()
