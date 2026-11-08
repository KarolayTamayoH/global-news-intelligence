"""Etapas reutilizables en Airflow y en una ejecución local, sin importar Airflow."""
import hashlib
import json
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.pipeline.artifacts import ArtifactStore
from src.validation.validate_gkg import validate_gkg, validate_target_date


def select_partition(conf, interval_end, run_id):
    target_date = (conf or {}).get('target_date')
    if target_date is None:
        if interval_end is None or interval_end.tzinfo is None:
            raise ValueError('Indica target_date cuando no haya intervalo con zona horaria')
        target_date = (interval_end.astimezone(timezone.utc) - timedelta(days=1)).strftime('%Y%m%d')
    validate_target_date(target_date)
    token = hashlib.sha256(run_id.encode()).hexdigest()[:20]
    return {'date': target_date, 'run_id': run_id,
            'prefix': f'runs/{target_date}/{token}'}


def update_history(info, fields, unset=None):
    from pymongo import MongoClient
    from src.config import MONGO_URI, MONGO_DATABASE
    with MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        update = {'$set': {'date': info['date'], **fields}}
        if unset:
            update['$unset'] = {key: '' for key in unset}
        client[MONGO_DATABASE]['pipeline_history'].update_one(
            {'_id': info['run_id']}, update, upsert=True)


@contextmanager
def stage(info, name):
    update_history(info, {f'stages.{name}.status': 'processing',
                          f'stages.{name}.started_at': datetime.now(timezone.utc)})
    try:
        yield
    except Exception as error:
        # Guardar el tipo; los mensajes de los clientes pueden contener direcciones o credenciales.
        update_history(info, {'status': 'failed', f'stages.{name}.status': 'failed',
                              f'stages.{name}.error_type': type(error).__name__})
        raise
    else:
        update_history(info, {f'stages.{name}.status': 'completed',
                              f'stages.{name}.completed_at': datetime.now(timezone.utc)},
                       unset=[f'stages.{name}.error_type'])


def extract_partition(info):
    from src.ingestion.download_gdelt import download_file
    from src.config import RAW_DIR
    filename = f"{info['date']}.gkg.csv.zip"
    update_history(info, {'status': 'processing', 'started_at': datetime.now(timezone.utc)})
    with stage(info, 'extract'), tempfile.TemporaryDirectory() as directory:
        # Reutilizar un ZIP local valido para pruebas historicas sin nueva descarga.
        raw_dir = RAW_DIR if (RAW_DIR / filename).exists() else Path(directory)
        path = download_file(filename, raw_dir=raw_dir)
        uri = ArtifactStore().publish(path, f"{info['prefix']}/raw/{filename}")
    return {**info, 'raw_uri': uri}


def validate_partition(info):
    filename = f"{info['date']}.gkg.csv.zip"
    with stage(info, 'validate'), tempfile.TemporaryDirectory() as directory:
        path = ArtifactStore().fetch(info['raw_uri'], Path(directory) / filename)
        validation = validate_gkg(path)
    return {**info, 'records': validation['total']}


def transform_partition(info):
    from src.transformation.transform_gkg import transform_file
    filename = f"{info['date']}.gkg.csv.zip"
    with stage(info, 'transform'), tempfile.TemporaryDirectory() as directory:
        path = ArtifactStore().fetch(info['raw_uri'], Path(directory) / filename)
        output = transform_file(path, output_dir=Path(directory) / 'processed')
        with output.open() as stream:
            records = sum(1 for line in stream if line.strip())
        if records != info['records']:
            raise ValueError('El JSONL no coincide con el conteo validado')
        uri = ArtifactStore().publish(output, f"{info['prefix']}/processed/{output.name}")
    return {**info, 'processed_uri': uri}


def load_mongo_partition(info):
    from pymongo import MongoClient
    from src.config import MONGO_URI, MONGO_DATABASE
    from src.ingestion.load_mongodb import load_mongodb
    with stage(info, 'mongodb'), tempfile.TemporaryDirectory() as directory:
        path = ArtifactStore().fetch(info['processed_uri'], Path(directory) / f"{info['date']}.jsonl")
        stats = load_mongodb(path)
        with MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) as client:
            database = client[MONGO_DATABASE]
            actual = database['gkg_records'].count_documents({'date': info['date']})
            if stats['processed'] != info['records'] or actual != info['records']:
                raise ValueError('Conteo MongoDB distinto del archivo validado')
            database['ingestion_history'].update_one(
                {'_id': f"{info['date']}.gkg.csv.zip"},
                {'$set': {'date': info['date'], 'status': 'completed',
                          'records': actual, **stats, 'completed_at': datetime.now(timezone.utc)},
                 '$unset': {'error': ''}}, upsert=True)
    return {**info, 'mongo_records': actual}


def aggregate_partition(info):
    from src.transformation.aggregate_snapshot import aggregate_snapshot
    with stage(info, 'cassandra'):
        aggregate_snapshot(info['date'])
    return {'date': info['date'], 'status': 'completed'}


def graph_partition(info):
    from src.ingestion.load_neo4j import load_neo4j
    with stage(info, 'neo4j'):
        # MERGE permite reparar nodos ausentes aunque exista un historial previo.
        load_neo4j(info['date'], force=True)
    return {'date': info['date'], 'status': 'completed'}


def finalize_partition(info):
    from scripts.verify_partition import verify_partition
    with stage(info, 'indicators'), tempfile.TemporaryDirectory() as directory:
        result = verify_partition(info['date'])
        if result['mongo_records'] != info['records']:
            raise ValueError('La reconciliacion no coincide con la particion validada')
        path = Path(directory) / 'indicators.json'
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        uri = ArtifactStore().publish(path, f"{info['prefix']}/reports/indicators.json")
    update_history(info, {'status': 'completed', 'records': result['mongo_records'],
                          'report_uri': uri, 'completed_at': datetime.now(timezone.utc)})
    return {'date': info['date'], 'records': result['mongo_records'],
            'status': 'completed', 'report_uri': uri}
