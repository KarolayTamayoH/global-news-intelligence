"""Publicar una versión completa de los KPIs sin borrar la versión visible."""
from collections import Counter
from datetime import datetime
import math
from uuid import uuid4

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.concurrent import execute_concurrent_with_args
from pymongo import MongoClient

from src.config import (MONGO_URI, MONGO_DATABASE, CASSANDRA_HOST,
                        CASSANDRA_PORT, CASSANDRA_KEYSPACE)
from src.validation.validate_gkg import validate_target_date


ENTITY_TABLES = {
    'theme': 'daily_theme_metrics_versions',
    'organization': 'daily_organization_metrics_versions',
}


def entity_counts(values):
    return {value.strip() for value in values
            if isinstance(value, str) and value.strip()}


def calculate_snapshot(records):
    themes, organizations = Counter(), Counter()
    total = tone_count = 0
    tone_sum = 0.0
    for record in records:
        total += 1
        themes.update(entity_counts(record.get('themes', [])))
        organizations.update(entity_counts(record.get('organizations', [])))
        try:
            tone = float(record.get('tone_raw', '').split(',')[0])
        except (AttributeError, TypeError, ValueError):
            continue
        if math.isfinite(tone):
            tone_sum += tone
            tone_count += 1
    if not total:
        raise ValueError('No hay registros para agregar')
    return {'total_records': total, 'unique_themes': len(themes),
            'average_tone': tone_sum / tone_count if tone_count else None,
            'themes': themes, 'organizations': organizations}


def read_entity_metrics(session, news_date, field, generation=None):
    """Leer una versión fija; None conserva compatibilidad con datos anteriores."""
    if field not in ENTITY_TABLES:
        raise ValueError('Entidad no permitida')
    table = ENTITY_TABLES[field]
    if generation is None:
        table = table.removesuffix('_versions')
        return session.execute(
            f'SELECT {field}, record_count FROM {table} WHERE news_date=%s',
            (news_date,))
    return session.execute(
        f'SELECT {field}, record_count FROM {table} '
        'WHERE news_date=%s AND generation=%s', (news_date, generation))


def active_entity_metrics(session, news_date, field):
    row = session.execute(
        "SELECT generation FROM daily_news_metrics "
        "WHERE metric_group='global' AND news_date=%s", (news_date,)).one()
    if row is None:
        return []
    return read_entity_metrics(session, news_date, field, row.generation)


def publish_snapshot(session, news_date, snapshot):
    """El único cambio visible es la última escritura de métricas y generación.

    Cada intento obtiene un UUID nuevo. Las versiones previas y los intentos
    incompletos se conservan para no invalidar lectores que ya tomaron su UUID.
    """
    generation = uuid4()
    for field, counts in [('theme', snapshot['themes']),
                          ('organization', snapshot['organizations'])]:
        statement = session.prepare(
            f'INSERT INTO {ENTITY_TABLES[field]} '
            f'(news_date, generation, {field}, record_count) VALUES (?, ?, ?, ?)')
        statement.consistency_level = ConsistencyLevel.LOCAL_QUORUM
        results = execute_concurrent_with_args(
            session, statement,
            ((news_date, generation, entity, count) for entity, count in counts.items()),
            concurrency=32, raise_on_first_error=True)
        # Comprobar también el resultado para clientes/adaptadores que no lancen.
        for success, result in results:
            if not success:
                raise RuntimeError('Carga de agregados incompleta') from result
        stored = {getattr(row, field): row.record_count
                  for row in read_entity_metrics(session, news_date, field, generation)}
        if stored != dict(counts):
            raise ValueError(f'Version incompleta de {field}')

    # Una sola mutación publica métricas y puntero conjuntamente.
    statement = session.prepare(
        'INSERT INTO daily_news_metrics '
        '(metric_group, news_date, total_records, unique_themes, average_tone, generation) '
        'VALUES (?, ?, ?, ?, ?, ?)')
    statement.consistency_level = ConsistencyLevel.LOCAL_QUORUM
    session.execute(statement, ('global', news_date, snapshot['total_records'],
                               snapshot['unique_themes'], snapshot['average_tone'], generation))
    return generation


def aggregate_snapshot(target_date=None):
    if target_date is not None:
        validate_target_date(target_date)
    with MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
        try:
            session = cluster.connect(CASSANDRA_KEYSPACE)
            session.default_consistency_level = ConsistencyLevel.LOCAL_QUORUM
            collection = client[MONGO_DATABASE]['gkg_records']
            dates = [target_date] if target_date else sorted(collection.distinct('date'))
            published = []
            for date_str in dates:
                validate_target_date(date_str)
                snapshot = calculate_snapshot(collection.find(
                    {'date': date_str}, {'themes': 1, 'organizations': 1, 'tone_raw': 1}))
                generation = publish_snapshot(
                    session, datetime.strptime(date_str, '%Y%m%d').date(), snapshot)
                published.append({'date': date_str, 'generation': str(generation),
                                  'records': snapshot['total_records']})
                print(f"Publicado {date_str}: {snapshot['total_records']:,} registros; {generation}")
            return published
        finally:
            cluster.shutdown()
