
from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"], port=9043)

try:
    session = cluster.connect("global_news_analytics")
    date = "2026-10-27"

    print(f"\nKPIs del {date}")

    # KPI 3: Top 10 temas
    themes = session.execute(
        """
        SELECT theme, record_count
        FROM daily_theme_metrics
        WHERE news_date = %s
        """,
        (date,)
    )

    top_themes = sorted(
        themes,
        key=lambda row: row.record_count,
        reverse=True
    )[:10]

    print("\nTOP 10 TEMAS")
    for index, row in enumerate(top_themes, 1):
        print(f"{index}. {row.theme}: {row.record_count:,}")

    # KPI 6: Top 10 organizaciones
    organizations = session.execute(
        """
        SELECT organization, record_count
        FROM daily_organization_metrics
        WHERE news_date = %s
        """,
        (date,)
    )

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
