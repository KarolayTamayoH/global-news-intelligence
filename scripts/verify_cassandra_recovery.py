"""Demostrar un fallo parcial y un reintento de Cassandra con bases reales.

Requiere una partición previamente reconciliada y migrada al modelo versionado.
Escribe una versión incompleta deliberada y la conserva sin hacerla visible.
"""
import argparse
import json
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch

from pymongo import MongoClient

from scripts.verify_partition import verify_partition
from src.config import ROOT, MONGO_URI, MONGO_DATABASE
from src.pipeline.tasks import select_partition, aggregate_partition, finalize_partition
from src.transformation import aggregate_snapshot


class InjectedInterruption(RuntimeError):
    pass


def verify_recovery(target_date):
    before = verify_partition(target_date)
    if before['cassandra_generation'] is None:
        raise ValueError('Migra primero la particion con aggregate_daily --date')
    info = select_partition({'target_date': target_date}, None, f'recovery__{uuid4()}')
    info['records'] = before['mongo_records']
    inserted = 0

    def interrupt(session, statement, parameters, **kwargs):
        nonlocal inserted
        # Escribir filas reales y fallar antes de publicar el nuevo UUID.
        for values in parameters:
            session.execute(statement, values)
            inserted += 1
            if inserted == 25:
                raise InjectedInterruption('Interrupcion controlada tras 25 escrituras')
        raise InjectedInterruption('Interrupcion controlada antes de publicar')

    with patch.object(aggregate_snapshot, 'execute_concurrent_with_args', side_effect=interrupt):
        try:
            aggregate_partition(info)
        except InjectedInterruption:
            pass
        else:
            raise AssertionError('No se produjo el fallo controlado')
    after_failure = verify_partition(target_date)
    if before != after_failure:
        raise AssertionError('El fallo cambio los indicadores visibles')
    with MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        failed = client[MONGO_DATABASE]['pipeline_history'].find_one({'_id': info['run_id']})
    if failed['status'] != 'failed' or failed['stages']['cassandra']['status'] != 'failed':
        raise AssertionError('El fallo no quedo registrado')
    if failed.get('report_uri') or failed.get('completed_at'):
        raise AssertionError('El intento fallido se marco como completo')

    aggregate_partition(info)
    result = finalize_partition(info)
    after_retry = verify_partition(target_date)
    if after_retry['cassandra_generation'] == before['cassandra_generation']:
        raise AssertionError('El reintento no publico una nueva generacion')
    comparison = {key: value for key, value in after_retry.items() if key != 'cassandra_generation'}
    if comparison != {key: value for key, value in before.items() if key != 'cassandra_generation'}:
        raise AssertionError('El reintento cambio los resultados esperados')
    with MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        recovered = client[MONGO_DATABASE]['pipeline_history'].find_one({'_id': info['run_id']})
    if recovered['status'] != 'completed' or recovered['stages']['cassandra']['status'] != 'completed':
        raise AssertionError('El reintento no quedo completo')
    if 'error_type' in recovered['stages']['cassandra']:
        raise AssertionError('El reintento conserva un error de etapa obsoleto')
    return {'status': 'verified', 'date': target_date, 'run_id': info['run_id'],
            'failure_after_rows': inserted, 'failed_attempt_status': failed['status'],
            'visible_metrics_preserved': True,
            'generation_before': before['cassandra_generation'],
            'generation_after_failure': after_failure['cassandra_generation'],
            'generation_after_retry': after_retry['cassandra_generation'],
            'retry_status': recovered['status'], 'report_uri': result['report_uri'],
            'verification': after_retry}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/cassandra_recovery_verification.json')
    args = parser.parse_args()
    if not args.output.is_absolute():
        args.output = ROOT / args.output
    result = verify_recovery(args.date)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f"Recuperacion verificada: {result['date']}; {result['failure_after_rows']} filas parciales invisibles")


if __name__ == '__main__':
    main()
