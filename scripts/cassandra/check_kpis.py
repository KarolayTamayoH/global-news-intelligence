
from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from src.transformation.aggregate_snapshot import active_entity_metrics
from src.config import CASSANDRA_HOST, CASSANDRA_PORT, CASSANDRA_KEYSPACE

cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)

try:
    session = cluster.connect(CASSANDRA_KEYSPACE)
    session.default_consistency_level = ConsistencyLevel.LOCAL_QUORUM
    date = "2026-10-27"

    print(f"\nKPIs del {date}")

    # KPI 3: Top 10 temas
    themes = active_entity_metrics(session, date, 'theme')

    top_themes = sorted(
        themes,
        key=lambda row: row.record_count,
        reverse=True
    )[:10]

    print("\nTOP 10 TEMAS")
    for index, row in enumerate(top_themes, 1):
        print(f"{index}. {row.theme}: {row.record_count:,}")

    # KPI 6: Top 10 organizaciones
    organizations = active_entity_metrics(session, date, 'organization')

    top_organizations = sorted(
        organizations,
        key=lambda row: row.record_count,
        reverse=True
    )[:10]

    print("\nTOP 10 ORGANIZACIONES")
    for index, row in enumerate(top_organizations, 1):
        print(
            f"{index}. {row.organization}: "
            f"{row.record_count:,}"
        )

finally:
    cluster.shutdown()
