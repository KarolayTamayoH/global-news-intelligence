"""Consultas acotadas para las vistas documentales y de relaciones."""
import re
from datetime import datetime

from src.config import MONGO_DATABASE, NEO4J_DATABASE
from src.validation.validate_gkg import validate_target_date


def get_document_dates(client):
    values = client[MONGO_DATABASE]['gkg_records'].distinct('date')
    dates = []
    for value in values:
        try:
            validate_target_date(value)
            dates.append(datetime.strptime(value, '%Y%m%d').date())
        except (ValueError, TypeError):
            continue
    return sorted(dates, reverse=True)


def search_documents(client, target_date, theme='', organization='', page=1, page_size=20):
    validate_target_date(target_date)
    if not 1 <= page_size <= 100 or page < 1:
        raise ValueError('Paginacion invalida')
    query = {'date': target_date}
    if theme.strip():
        query['themes'] = theme.strip()[:128]
    if organization.strip():
        query['organizations'] = {'$regex': re.escape(organization.strip()[:128]), '$options': 'i'}
    collection = client[MONGO_DATABASE]['gkg_records']
    total = collection.count_documents(query)
    cursor = collection.find(query).sort('_id', 1).skip((page - 1) * page_size).limit(page_size)
    documents = list(cursor)
    for document in documents:
        document['_id'] = str(document['_id'])
    return {'total': total, 'documents': documents}


def get_graph_counts(driver, target_date):
    validate_target_date(target_date)
    patterns = {
        'records': '(r:GKGRecord {date: $date})',
        'themes': '(r:GKGRecord {date: $date})-[:HAS_THEME]->(:Theme)',
        'organizations': '(r:GKGRecord {date: $date})-[:MENTIONS_ORG]->(:Organization)',
    }
    with driver.session(database=NEO4J_DATABASE) as session:
        return {name: session.run(f'MATCH {pattern} RETURN count(*) AS total',
                                 date=target_date).single()['total']
                for name, pattern in patterns.items()}


def get_graph_sample(driver, target_date, entity_type='Theme', entity_name='', record_limit=3):
    validate_target_date(target_date)
    if entity_type not in ('Theme', 'Organization') or not 1 <= record_limit <= 5:
        raise ValueError('Filtro de grafo invalido')
    # Las etiquetas y tipos proceden de esta lista cerrada; el texto del usuario es parametro.
    patterns = {
        'Theme': '(r)-[:HAS_THEME]->(:Theme {name: $entity_name})',
        'Organization': '(r)-[:MENTIONS_ORG]->(:Organization {name: $entity_name})',
    }
    condition = f'WHERE EXISTS {{ MATCH {patterns[entity_type]} }}' if entity_name.strip() else ''
    query = f'''
    MATCH (r:GKGRecord {{date: $date}})
    {condition}
    WITH r ORDER BY r.id LIMIT $record_limit
    OPTIONAL MATCH (r)-[rel:HAS_THEME|MENTIONS_ORG]->(entity)
    RETURN r.id AS record_id, labels(entity)[0] AS entity_type,
           entity.name AS entity_name, type(rel) AS relationship
    ORDER BY record_id, entity_type, entity_name
    '''
    with driver.session(database=NEO4J_DATABASE) as session:
        return session.run(query, date=target_date, entity_name=entity_name.strip()[:256],
                           record_limit=record_limit).data()
