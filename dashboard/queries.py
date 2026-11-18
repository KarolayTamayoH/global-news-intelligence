"""Consultas acotadas para las vistas documentales y de relaciones."""
import re
from datetime import datetime

from src.config import MONGO_DATABASE, NEO4J_DATABASE
from src.validation.validate_gkg import validate_target_date

# Lista cerrada: etiquetas y tipos de relacion nunca provienen del usuario.
ENTITY_SPECS = {
    'Theme': ('HAS_THEME', 'Theme'),
    'Organization': ('MENTIONS_ORG', 'Organization'),
}


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


# ---------------------------------------------------------------------------
# KPIs de red (Neo4j)
# ---------------------------------------------------------------------------
def get_graph_overview(driver, target_date):
    """Por tipo de entidad: entidades unicas, menciones, menciones del top 10 y entidades de una sola mencion."""
    validate_target_date(target_date)
    result = {}
    with driver.session(database=NEO4J_DATABASE) as session:
        for entity_type, (relation, label) in ENTITY_SPECS.items():
            record = session.run(f'''
            MATCH (r:GKGRecord {{date: $date}})-[:{relation}]->(e:{label})
            WITH e, count(r) AS n ORDER BY n DESC
            WITH collect(n) AS counts
            RETURN size(counts) AS entities,
                   reduce(s = 0, c IN counts | s + c) AS mentions,
                   reduce(s = 0, c IN counts[0..10] | s + c) AS top10,
                   size([c IN counts WHERE c = 1]) AS singletons
            ''', date=target_date).single()
            result[entity_type] = dict(record)
    return result


def get_degree_distribution(driver, target_date):
    """Cuantos registros tienen cada numero de conexiones (temas + organizaciones)."""
    validate_target_date(target_date)
    with driver.session(database=NEO4J_DATABASE) as session:
        return session.run('''
        MATCH (r:GKGRecord {date: $date})
        OPTIONAL MATCH (r)-[x:HAS_THEME|MENTIONS_ORG]->()
        WITH r, count(x) AS degree
        RETURN degree, count(*) AS records ORDER BY degree
        ''', date=target_date).data()


def get_top_entities(driver, target_date, entity_type='Organization', limit=25):
    validate_target_date(target_date)
    if entity_type not in ENTITY_SPECS or not 1 <= limit <= 100:
        raise ValueError('Parametros de entidad invalidos')
    relation, label = ENTITY_SPECS[entity_type]
    with driver.session(database=NEO4J_DATABASE) as session:
        return session.run(f'''
        MATCH (r:GKGRecord {{date: $date}})-[:{relation}]->(e:{label})
        RETURN e.name AS name, count(r) AS records
        ORDER BY records DESC, name LIMIT $limit
        ''', date=target_date, limit=limit).data()


def get_org_cooccurrence(driver, target_date, top_n=40, limit=10):
    """Pares de organizaciones que aparecen juntas, restringido a las top_n mas mencionadas
    para mantener la consulta acotada."""
    validate_target_date(target_date)
    if not 10 <= top_n <= 100 or not 1 <= limit <= 25:
        raise ValueError('Parametros de co-ocurrencia invalidos')
    with driver.session(database=NEO4J_DATABASE) as session:
        return session.run('''
        MATCH (r:GKGRecord {date: $date})-[:MENTIONS_ORG]->(o:Organization)
        WITH o, count(r) AS mentions ORDER BY mentions DESC LIMIT $top_n
        WITH collect(o) AS tops
        MATCH (r:GKGRecord {date: $date})-[:MENTIONS_ORG]->(x:Organization)
        WHERE x IN tops
        WITH r, collect(x) AS members WHERE size(members) > 1
        UNWIND members AS a
        UNWIND members AS b
        WITH a, b WHERE a.name < b.name
        RETURN a.name AS source, b.name AS target, count(*) AS records
        ORDER BY records DESC, source, target LIMIT $limit
        ''', date=target_date, top_n=top_n, limit=limit).data()


def get_entity_profile(driver, target_date, entity_type, entity_name, limit=10):
    """Organizacion -> temas con los que se asocia; Tema -> organizaciones que lo protagonizan."""
    validate_target_date(target_date)
    if entity_type not in ENTITY_SPECS or not entity_name.strip() or not 1 <= limit <= 25:
        raise ValueError('Perfil de entidad invalido')
    source_relation, source_label = ENTITY_SPECS[entity_type]
    other_type = 'Theme' if entity_type == 'Organization' else 'Organization'
    other_relation, other_label = ENTITY_SPECS[other_type]
    name = entity_name.strip()[:256]
    with driver.session(database=NEO4J_DATABASE) as session:
        total = session.run(f'''
        MATCH (r:GKGRecord {{date: $date}})-[:{source_relation}]->(:{source_label} {{name: $name}})
        RETURN count(r) AS total
        ''', date=target_date, name=name).single()['total']
        related = session.run(f'''
        MATCH (r:GKGRecord {{date: $date}})-[:{source_relation}]->(:{source_label} {{name: $name}})
        MATCH (r)-[:{other_relation}]->(e:{other_label})
        RETURN e.name AS name, count(r) AS records
        ORDER BY records DESC, name LIMIT $limit
        ''', date=target_date, name=name, limit=limit).data()
    return {'total': total, 'related': related, 'related_type': other_type}
