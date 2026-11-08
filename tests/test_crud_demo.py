import unittest
from unittest.mock import MagicMock, patch

from scripts import crud_demo


class CrudCleanupTests(unittest.TestCase):
    def test_mongodb_cleanup_uses_only_own_id_on_failed_verification(self):
        client = MagicMock()
        collection = client.__enter__.return_value.__getitem__.return_value.__getitem__.return_value
        collection.find_one.return_value = None
        with patch.object(crud_demo, 'MongoClient', return_value=client):
            with self.assertRaisesRegex(ValueError, 'lectura incorrecta'):
                crud_demo.mongodb_crud()
        inserted = collection.insert_one.call_args.args[0]['_id']
        collection.delete_one.assert_called_once_with({'_id': inserted})
        self.assertTrue(inserted.startswith('crud-'))

    def test_neo4j_cleanup_is_limited_to_demo_label_and_own_run(self):
        driver = MagicMock()
        session = driver.__enter__.return_value.session.return_value.__enter__.return_value
        session.run.return_value.single.return_value = None
        with patch.object(crud_demo, 'NEO4J_PASSWORD', 'test-only'), \
             patch.object(crud_demo.GraphDatabase, 'driver', return_value=driver), \
             self.assertRaisesRegex(ValueError, 'lectura incorrecta'):
            crud_demo.neo4j_crud()
        query, = session.run.call_args.args
        self.assertEqual(query, 'MATCH (n:CrudDemo {run_id:$id}) DETACH DELETE n')
        self.assertTrue(session.run.call_args.kwargs['id'].startswith('crud-'))


if __name__ == '__main__':
    unittest.main()
