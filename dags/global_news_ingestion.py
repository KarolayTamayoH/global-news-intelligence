"""Ingesta diaria GKG: archivos compartidos, tres modelos y KPIs reconciliados."""
from datetime import datetime, timedelta, timezone

from airflow.decorators import dag, task


@dag(
    dag_id='global_news_ingestion',
    description='GDELT GKG: extraccion, validacion, MongoDB, Cassandra, Neo4j e indicadores',
    schedule='0 6 * * *',
    start_date=datetime(2026, 10, 1, tzinfo=timezone.utc),
    catchup=False,
    is_paused_upon_creation=True,
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=4),
    default_args={'retries': 2, 'retry_delay': timedelta(minutes=5)},
    tags=['gdelt', 'big-data', 'global-news'],
)
def global_news_ingestion():
    @task
    def select_partition(**context):
        from src.pipeline.tasks import select_partition as select
        conf = context['dag_run'].conf or {}
        return select(conf, context.get('data_interval_end'), context['run_id'])

    @task
    def extract(info):
        from src.pipeline.tasks import extract_partition
        return extract_partition(info)

    @task
    def validate(info):
        from src.pipeline.tasks import validate_partition
        return validate_partition(info)

    @task
    def transform(info):
        from src.pipeline.tasks import transform_partition
        return transform_partition(info)

    @task
    def load_mongodb(info):
        from src.pipeline.tasks import load_mongo_partition
        return load_mongo_partition(info)

    @task
    def aggregate_cassandra(info):
        from src.pipeline.tasks import aggregate_partition
        return aggregate_partition(info)

    @task
    def load_neo4j(info):
        from src.pipeline.tasks import graph_partition
        return graph_partition(info)

    @task
    def generate_indicators(info, cassandra_result, neo4j_result):
        from src.pipeline.tasks import finalize_partition
        # Estos argumentos establecen la dependencia de ambas ramas.
        if any(result['status'] != 'completed' for result in (cassandra_result, neo4j_result)):
            raise ValueError('Las cargas de las bases no finalizaron')
        return finalize_partition(info)

    selected = select_partition()
    extracted = extract(selected)
    validated = validate(extracted)
    transformed = transform(validated)
    loaded = load_mongodb(transformed)
    aggregated = aggregate_cassandra(loaded)
    graph = load_neo4j(loaded)
    generate_indicators(loaded, aggregated, graph)


dag = global_news_ingestion()
