import json
import unittest
from unittest.mock import MagicMock, patch

from scripts import bootstrap_databases as bootstrap
from src.config import ROOT
from src.transformation.transform_gkg import transform_record
from src.validation.validate_gkg import EXPECTED_COLUMNS


class BootstrapTests(unittest.TestCase):
    def test_mongodb_repeat_preserves_existing_collections(self):
        client = MagicMock()
        database = client.__enter__.return_value.__getitem__.return_value
        database.list_collection_names.return_value = [
            'gkg_records', 'ingestion_history', 'neo4j_ingestion_history', 'pipeline_history']
        with patch.object(bootstrap, 'MongoClient', return_value=client):
            bootstrap.bootstrap_mongodb()
            bootstrap.bootstrap_mongodb()
        database.create_collection.assert_not_called()
        self.assertEqual(database.command.call_count, 2)
        self.assertEqual(database.command.call_args.args, ('collMod', 'gkg_records'))
        self.assertEqual(database.command.call_args.kwargs['validationAction'], 'error')

    def test_schema_accepts_a_transformed_document_and_rejects_bad_types(self):
        # MongoDB's bsonType is adapted to JSON Schema for this local contract check.
        from jsonschema import Draft4Validator
        bson_to_json = {'object': 'object', 'array': 'array', 'string': 'string',
                        'int': 'integer', 'long': 'integer'}

        def adapt(value):
            if isinstance(value, dict):
                output = {key: adapt(item) for key, item in value.items() if key != 'bsonType'}
                if 'bsonType' in value:
                    kinds = value['bsonType']
                    output['type'] = (list(set(bson_to_json[k] for k in kinds))
                                      if isinstance(kinds, list) else bson_to_json[kinds])
                return output
            return value

        schema = adapt(json.loads((ROOT / 'scripts/mongodb/schema.json').read_text()))
        record = transform_record(dict(zip(EXPECTED_COLUMNS, ['20261027', '1'] + [''] * 9)),
                                  '20261027.gkg.csv.zip', 1)
        validator = Draft4Validator(schema)
        self.assertEqual(list(validator.iter_errors(record)), [])
        record['num_articles'] = '1'
        self.assertTrue(list(validator.iter_errors(record)))
        self.assertEqual(len(bootstrap.ddl_statements(ROOT / 'scripts/cassandra/schema.cql')), 4)
        self.assertEqual(len(bootstrap.ddl_statements(ROOT / 'scripts/neo4j/schema.cypher')), 4)


if __name__ == '__main__':
    unittest.main()
