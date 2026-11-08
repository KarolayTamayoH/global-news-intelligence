"""Demostrar CRUD con identificadores unicos, aislados de registros GKG y KPIs."""
import argparse
import json
from pathlib import Path
from uuid import uuid4

from cassandra.cluster import Cluster
from neo4j import GraphDatabase
from pymongo import MongoClient

from src.config import (MONGO_URI, MONGO_DATABASE, CASSANDRA_HOST, CASSANDRA_PORT,
                        CASSANDRA_KEYSPACE, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mongodb_crud():
    identifier = f'crud-{uuid4().hex}'
    with MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        collection = client[MONGO_DATABASE]['crud_demo']
        try:
            collection.insert_one({'_id': identifier, 'value': 1, 'purpose': 'course-demo'})
            created = collection.find_one({'_id': identifier})
            require(created is not None and created['value'] == 1, 'MongoDB: insercion/lectura incorrecta')
            updated = collection.update_one({'_id': identifier}, {'$set': {'value': 2}})
            require(updated.modified_count == 1 and collection.find_one({'_id': identifier})['value'] == 2,
                    'MongoDB: actualizacion incorrecta')
            deleted = collection.delete_one({'_id': identifier})
            require(deleted.deleted_count == 1 and collection.find_one({'_id': identifier}) is None,
                    'MongoDB: eliminacion incorrecta')
        finally:
            # La clave UUID pertenece exclusivamente a esta ejecucion.
            collection.delete_one({'_id': identifier})
    return {'id': identifier, 'create': True, 'read': True, 'update': True, 'delete': True,
            'values': [1, 2], 'test_data_removed': True}


def cassandra_crud():
    identifier = uuid4()
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
    session = None
    try:
        session = cluster.connect(CASSANDRA_KEYSPACE)
        session.execute('''CREATE TABLE IF NOT EXISTS crud_demo (
            id uuid PRIMARY KEY, value int, purpose text)''')
        try:
            session.execute('INSERT INTO crud_demo (id, value, purpose) VALUES (%s, %s, %s)',
                            (identifier, 1, 'course-demo'))
            created = session.execute('SELECT value FROM crud_demo WHERE id=%s', (identifier,)).one()
            require(created is not None and created.value == 1, 'Cassandra: insercion/lectura incorrecta')
            session.execute('UPDATE crud_demo SET value=%s WHERE id=%s', (2, identifier))
            updated = session.execute('SELECT value FROM crud_demo WHERE id=%s', (identifier,)).one()
            require(updated is not None and updated.value == 2, 'Cassandra: actualizacion incorrecta')
            session.execute('DELETE FROM crud_demo WHERE id=%s', (identifier,))
            require(session.execute('SELECT value FROM crud_demo WHERE id=%s', (identifier,)).one() is None,
                    'Cassandra: eliminacion incorrecta')
        finally:
            session.execute('DELETE FROM crud_demo WHERE id=%s', (identifier,))
    finally:
        cluster.shutdown()
    return {'id': str(identifier), 'create': True, 'read': True, 'update': True, 'delete': True,
            'values': [1, 2], 'test_data_removed': True}


def neo4j_crud():
    if not NEO4J_PASSWORD:
        raise ValueError('Configura NEO4J_PASSWORD en el entorno')
    identifier = f'crud-{uuid4().hex}'
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            try:
                session.run('''CREATE (a:CrudDemo {run_id:$id, kind:'record', value:1}),
                                     (b:CrudDemo {run_id:$id, kind:'entity'})''', id=identifier).consume()
                session.run('''MATCH (a:CrudDemo {run_id:$id, kind:'record'}),
                                     (b:CrudDemo {run_id:$id, kind:'entity'})
                               CREATE (a)-[:DEMO_RELATION {value:1}]->(b)''', id=identifier).consume()
                created = session.run('''MATCH (a:CrudDemo {run_id:$id})-[r:DEMO_RELATION]->
                                               (:CrudDemo {run_id:$id})
                                        RETURN a.value AS value, count(r) AS total''', id=identifier).single()
                require(created is not None and created['total'] == 1 and created['value'] == 1,
                        'Neo4j: creacion/lectura incorrecta')
                session.run('''MATCH (a:CrudDemo {run_id:$id})-[r:DEMO_RELATION]->
                                      (:CrudDemo {run_id:$id}) SET a.value=2, r.value=2''', id=identifier).consume()
                updated = session.run('''MATCH (a:CrudDemo {run_id:$id})-[r:DEMO_RELATION]->
                                               (:CrudDemo {run_id:$id})
                                        RETURN a.value AS node_value, r.value AS relationship_value''',
                                      id=identifier).single()
                require(updated is not None and updated['node_value'] == updated['relationship_value'] == 2,
                        'Neo4j: actualizacion incorrecta')
                session.run('''MATCH (:CrudDemo {run_id:$id})-[r:DEMO_RELATION]->
                                      (:CrudDemo {run_id:$id}) DELETE r''', id=identifier).consume()
                relationships = session.run('''MATCH (:CrudDemo {run_id:$id})-[r:DEMO_RELATION]->()
                                              RETURN count(r) AS total''', id=identifier).single()['total']
                require(relationships == 0, 'Neo4j: la relacion no se elimino')
                session.run('MATCH (n:CrudDemo {run_id:$id}) DETACH DELETE n', id=identifier).consume()
                remaining = session.run('MATCH (n:CrudDemo {run_id:$id}) RETURN count(n) AS total',
                                        id=identifier).single()['total']
                require(remaining == 0, 'Neo4j: quedaron nodos de prueba')
            finally:
                session.run('MATCH (n:CrudDemo {run_id:$id}) DETACH DELETE n', id=identifier).consume()
    return {'id': identifier, 'create': True, 'create_relationship': True, 'read': True,
            'update': True, 'delete_relationship': True, 'delete': True,
            'values': [1, 2], 'test_data_removed': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', choices=['all', 'mongodb', 'cassandra', 'neo4j'], default='all')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.database in ('all', 'neo4j') and not NEO4J_PASSWORD:
        parser.error('Carga NEO4J_PASSWORD antes de ejecutar la demostracion')
    actions = {'mongodb': mongodb_crud, 'cassandra': cassandra_crud, 'neo4j': neo4j_crud}
    results = {name: action() for name, action in actions.items() if args.database in ('all', name)}
    text = json.dumps({'status': 'verified', 'databases': results}, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text)


if __name__ == '__main__':
    main()
