"""Guardar evidencia de una ejecución programada y reconciliada de Airflow.

Ejecutar dentro del contenedor Airflow. No dispara ni modifica ejecuciones.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def verify_scheduled_run(run_id=None):
    from airflow.models import DagRun
    from airflow.utils.session import create_session
    from airflow.utils.types import DagRunType
    from pymongo import MongoClient
    from scripts.verify_partition import verify_partition
    from src.config import MONGO_URI, MONGO_DATABASE

    expected = {'select_partition', 'extract', 'validate', 'transform',
                'load_mongodb', 'aggregate_cassandra', 'load_neo4j',
                'generate_indicators'}
    with create_session() as session:
        query = session.query(DagRun).filter(
            DagRun.dag_id == 'global_news_ingestion',
            DagRun.run_type == DagRunType.SCHEDULED,
        )
        if run_id:
            query = query.filter(DagRun.run_id == run_id)
        run = query.order_by(DagRun.execution_date.desc()).first()
        if run is None:
            raise ValueError('Todavia no existe una ejecucion programada')
        states = {task.task_id: str(task.state)
                  for task in run.get_task_instances(session=session)}
        if str(run.state) != 'success' or set(states) != expected or any(
                state != 'success' for state in states.values()):
            raise ValueError(f'Ejecucion programada incompleta: {states}')
        result = {'dag_id': run.dag_id, 'run_id': run.run_id,
                  'run_type': 'scheduled', 'state': str(run.state),
                  'verified_at': datetime.now(timezone.utc).isoformat(),
                  'started_at': run.start_date.isoformat() if run.start_date else None,
                  'ended_at': run.end_date.isoformat() if run.end_date else None,
                  'data_interval_start': run.data_interval_start.isoformat(),
                  'data_interval_end': run.data_interval_end.isoformat(),
                  'task_states': states}
    with MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        history = client[MONGO_DATABASE]['pipeline_history'].find_one(
            {'_id': result['run_id']})
    if not history or history.get('status') != 'completed':
        raise ValueError('La ejecucion no tiene historial reconciliado completo')
    result['verification'] = verify_partition(history['date'])
    result['report_uri'] = history['report_uri']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    from src.config import ROOT
    if not args.output.is_absolute():
        args.output = ROOT / args.output
    result = verify_scheduled_run(args.run_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f"Ejecucion programada verificada: {result['run_id']}")


if __name__ == '__main__':
    main()
