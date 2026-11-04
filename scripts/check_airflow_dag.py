"""Comprobar importacion/topologia y, opcionalmente, ejecutar un DAG real en Airflow 2.11.1."""
import argparse
import json
import tempfile
from pathlib import Path

from src.config import ROOT


def main():
    from airflow import __version__
    from airflow.models import DagBag
    import pendulum

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--date', default='20261027')
    parser.add_argument('--execution-date', default='2026-10-28T06:00:00+00:00')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--graph-output', type=Path, help='Exportar dependencias reales como DOT')
    args = parser.parse_args()
    for name in ('output', 'graph_output'):
        path = getattr(args, name)
        if path is not None and not path.is_absolute():
            setattr(args, name, ROOT / path)
    bag = DagBag(dag_folder=str(ROOT / 'dags'), include_examples=False, safe_mode=False)
    if bag.import_errors:
        raise RuntimeError(f'Errores al importar DAG: {bag.import_errors}')
    dag = bag.get_dag('global_news_ingestion')
    expected = {'select_partition', 'extract', 'validate', 'transform', 'load_mongodb',
                'aggregate_cassandra', 'load_neo4j', 'generate_indicators'}
    if dag is None or set(dag.task_ids) != expected:
        raise ValueError('El DAG no contiene las ocho etapas esperadas')
    if not {'aggregate_cassandra', 'load_neo4j'}.issubset(
            dag.get_task('generate_indicators').upstream_task_ids):
        raise ValueError('La reconciliacion debe esperar ambas ramas')
    if dag.schedule_interval != '0 6 * * *' or dag.catchup or dag.max_active_runs != 1:
        raise ValueError('Programacion o concurrencia distintas de la configuracion esperada')
    if args.graph_output:
        lines = ['digraph DAG {', 'rankdir=TB;', 'node [shape=box, style=rounded];']
        for task in dag.tasks:
            lines.append(f'  {json.dumps(task.task_id)};')
            for child in sorted(task.downstream_task_ids):
                lines.append(f'  {json.dumps(task.task_id)} -> {json.dumps(child)};')
        lines.append('}')
        args.graph_output.parent.mkdir(parents=True, exist_ok=True)
        args.graph_output.write_text('\n'.join(lines) + '\n')
    result = {'airflow_version': __version__, 'dag_id': dag.dag_id,
              'schedule_utc': dag.schedule_interval, 'tasks': sorted(dag.task_ids),
              'import_errors': 0}
    if args.run:
        run = dag.test(execution_date=pendulum.parse(args.execution_date),
                       run_conf={'target_date': args.date})
        states = {task.task_id: str(task.state) for task in run.get_task_instances()}
        if str(run.state) != 'success' or set(states) != expected or any(
                state != 'success' for state in states.values()):
            raise ValueError(f'La ejecucion del DAG no termino correctamente: {states}')
        from pymongo import MongoClient
        from src.config import MONGO_URI, MONGO_DATABASE
        from src.pipeline.artifacts import ArtifactStore
        with MongoClient(MONGO_URI) as client:
            history = client[MONGO_DATABASE]['pipeline_history'].find_one({'_id': run.run_id})
        if not history or history.get('status') != 'completed':
            raise ValueError('Falta historial completo del pipeline')
        with tempfile.TemporaryDirectory() as directory:
            path = ArtifactStore().fetch(history['report_uri'], Path(directory) / 'indicators.json')
            indicators = json.loads(path.read_text())
        result.update({'date': args.date, 'run_id': run.run_id, 'state': str(run.state),
                       'execution_date': args.execution_date, 'task_states': states,
                       'pipeline_status': history['status'], 'report_uri': history['report_uri'],
                       'verification': indicators})
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text)


if __name__ == '__main__':
    main()
