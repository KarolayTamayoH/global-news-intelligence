"""Reconciliar una fecha en las tres bases sin modificar registros."""
import argparse
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

from cassandra.cluster import Cluster
from neo4j import GraphDatabase
from pymongo import MongoClient

from src.config import (
    MONGO_URI, MONGO_DATABASE, CASSANDRA_HOST, CASSANDRA_PORT,
    CASSANDRA_KEYSPACE, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE,
)
from src.validation.validate_gkg import validate_target_date
from src.transformation.aggregate_snapshot import read_entity_metrics
from cassandra import ConsistencyLevel


def entities(values):
    return {v.strip() for v in values if isinstance(v, str) and v.strip()}


def verify_partition(target_date):
    validate_target_date(target_date)
    if not NEO4J_PASSWORD:
        raise ValueError('Configura NEO4J_PASSWORD en el entorno')
    themes, organizations = Counter(), Counter()
    records = tone_count = theme_edges = org_edges = 0
    tone_sum = 0.0
    with MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        collection = client[MONGO_DATABASE]['gkg_records']
        for record in collection.find({'date': target_date},
                                      {'themes': 1, 'organizations': 1, 'tone_raw': 1}):
            records += 1
            themes.update(entities(record.get('themes', [])))
            organizations.update(entities(record.get('organizations', [])))
            theme_edges += len(entities(record.get('themes', [])[:10]))
            org_edges += len(entities(record.get('organizations', [])[:10]))
            try:
                tone = float(record.get('tone_raw', '').split(',')[0])
                if not math.isfinite(tone):
                    continue
                tone_sum += tone
                tone_count += 1
            except (TypeError, ValueError):
                pass
        index_names = sorted(collection.index_information())
    if records == 0:
        raise ValueError('La particion no contiene documentos en MongoDB')
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
    try:
        session = cluster.connect(CASSANDRA_KEYSPACE)
        session.default_consistency_level = ConsistencyLevel.LOCAL_QUORUM
        news_date = datetime.strptime(target_date, '%Y%m%d').date()
        daily = session.execute(
            "SELECT total_records, unique_themes, average_tone, generation FROM daily_news_metrics "
            "WHERE metric_group='global' AND news_date=%s", (news_date,)).one()
        if daily is None or daily.total_records != records or daily.unique_themes != len(themes):
            raise ValueError('Metricas diarias Cassandra distintas de MongoDB')
        previous = session.execute(
            "SELECT total_records FROM daily_news_metrics WHERE metric_group='global' "
            "AND news_date < %s LIMIT 1", (news_date,)).one()
        variation = (100 * (records - previous.total_records) / previous.total_records
                     if previous and previous.total_records > 0 else None)
        expected_tone = tone_sum / tone_count if tone_count else None
        if (expected_tone is None and daily.average_tone is not None) or (
            expected_tone is not None and (daily.average_tone is None or
                not math.isclose(expected_tone, daily.average_tone, abs_tol=1e-10))):
            raise ValueError('Tono medio distinto entre MongoDB y Cassandra')
        for table, field, expected in [
            ('daily_theme_metrics', 'theme', themes),
            ('daily_organization_metrics', 'organization', organizations),
        ]:
            rows = read_entity_metrics(session, news_date, field, daily.generation)
            actual = {getattr(row, field): row.record_count for row in rows}
            if actual != dict(expected):
                raise ValueError(f'Agregados de {table} distintos de MongoDB')
    finally:
        cluster.shutdown()
    graph = {}
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            for key, pattern, expected in [
                ('records', '(r:GKGRecord {date:$date})', records),
                ('theme_edges', '(r:GKGRecord {date:$date})-[:HAS_THEME]->(:Theme)', theme_edges),
                ('organization_edges', '(r:GKGRecord {date:$date})-[:MENTIONS_ORG]->(:Organization)', org_edges),
            ]:
                stored = session.run(f'MATCH {pattern} RETURN count(*) AS total', date=target_date).single()['total']
                if stored != expected:
                    raise ValueError(f'Conteo Neo4j {key}: {stored}; esperado: {expected}')
                graph[key] = stored
    return {'date': target_date, 'mongo_records': records, 'mongo_indexes': index_names,
            'unique_themes': len(themes), 'unique_organizations': len(organizations),
            'average_tone': expected_tone, 'cassandra_records': daily.total_records,
            'cassandra_entities_match': True,
            'cassandra_generation': str(daily.generation) if daily.generation else None,
            'neo4j': graph,
             'graph_entity_limit_per_record': 10, 'status': 'verified',
            'kpis': {'daily_records': records, 'variation_pct': variation,
                     'unique_themes': len(themes), 'average_tone': expected_tone,
                     'top_themes': sorted(themes.items(), key=lambda pair: (-pair[1], pair[0]))[:10],
                     'top_organizations': sorted(organizations.items(), key=lambda pair: (-pair[1], pair[0]))[:10]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', required=True)
    parser.add_argument('--output', type=Path, help='Guardar resumen JSON sin credenciales')
    args = parser.parse_args()
    result = verify_partition(args.date)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text)


if __name__ == '__main__':
    main()
