"""Crear/actualizar esquemas e índices sin borrar colecciones, tablas o datos.

Ejecutar desde la raíz: python -m scripts.bootstrap_databases
"""
import argparse
import json

from cassandra.cluster import Cluster
from neo4j import GraphDatabase
from pymongo import MongoClient

from src.config import (
    ROOT, MONGO_URI, MONGO_DATABASE, CASSANDRA_HOST, CASSANDRA_PORT,
    CASSANDRA_KEYSPACE, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE,
)


def ddl_statements(path):
    # Los DDL versionados no contienen ';' dentro de literales.
    text = '\n'.join(line for line in path.read_text().splitlines()
                     if not line.lstrip().startswith('//') and not line.lstrip().startswith('--'))
    return [part.strip() for part in text.split(';') if part.strip()]


def bootstrap_mongodb():
    schema = json.loads((ROOT / 'scripts/mongodb/schema.json').read_text())
    with MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        client.admin.command('ping')
        database = client[MONGO_DATABASE]
        options = {'validator': {'$jsonSchema': schema},
                   'validationLevel': 'strict', 'validationAction': 'error'}
        if 'gkg_records' not in database.list_collection_names():
            database.create_collection('gkg_records', **options)
        else:
            database.command('collMod', 'gkg_records', **options)
        database['gkg_records'].create_index([('date', 1), ('_id', 1)], name='date_id')
        database['gkg_records'].create_index('source_file', name='source_file')
        for name in ['ingestion_history', 'neo4j_ingestion_history']:
            if name not in database.list_collection_names():
                database.create_collection(name)
        database['ingestion_history'].create_index([('date', 1), ('status', 1)], name='date_status')
    print('MongoDB: esquema e indices listos')


def bootstrap_cassandra():
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
    try:
        session = cluster.connect()
        for query in ddl_statements(ROOT / 'scripts/cassandra/schema.cql'):
            session.execute(query.replace('global_news_analytics', CASSANDRA_KEYSPACE))
    finally:
        cluster.shutdown()
    print('Cassandra: keyspace y tablas listos')


def bootstrap_neo4j():
    if not NEO4J_PASSWORD:
        raise ValueError('Configura NEO4J_PASSWORD en el entorno del proceso')
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        driver.verify_connectivity()
        with driver.session(database=NEO4J_DATABASE) as session:
            for query in ddl_statements(ROOT / 'scripts/neo4j/schema.cypher'):
                session.run(query).consume()
    print('Neo4j: restricciones listas')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', choices=['all', 'mongodb', 'cassandra', 'neo4j'], default='all')
    args = parser.parse_args()
    actions = {'mongodb': bootstrap_mongodb, 'cassandra': bootstrap_cassandra, 'neo4j': bootstrap_neo4j}
    if args.database in ('all', 'neo4j') and not NEO4J_PASSWORD:
        parser.error('Carga NEO4J_PASSWORD en el entorno antes de inicializar Neo4j')
    for name, action in actions.items():
        if args.database in ('all', name):
            action()


if __name__ == '__main__':
    main()
