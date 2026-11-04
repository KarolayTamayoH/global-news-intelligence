"""Ejecutar las mismas etapas del DAG en terminal, sin instalar Airflow."""
import argparse
import json
from datetime import datetime, timezone

from src.pipeline.tasks import (
    select_partition, extract_partition, validate_partition, transform_partition,
    load_mongo_partition, aggregate_partition, graph_partition, finalize_partition,
)


def run_pipeline(target_date, run_id=None):
    run_id = run_id or f'local__{datetime.now(timezone.utc).isoformat()}'
    info = select_partition({'target_date': target_date}, None, run_id)
    info = extract_partition(info)
    info = validate_partition(info)
    info = transform_partition(info)
    info = load_mongo_partition(info)
    aggregate_partition(info)
    graph_partition(info)
    return finalize_partition(info)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', required=True)
    parser.add_argument('--run-id', help='Identificador estable al repetir un intento')
    args = parser.parse_args()
    print(json.dumps(run_pipeline(args.date, args.run_id), indent=2))


if __name__ == '__main__':
    main()
