
from collections import Counter
from datetime import datetime

from pymongo import MongoClient
from cassandra.cluster import Cluster


MONGO_URI = "mongodb://localhost:27018/"
CASSANDRA_HOST = "127.0.0.1"
CASSANDRA_PORT = 9043


def aggregate_entities():
    mongo_client = MongoClient(MONGO_URI)
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)

    try:
        collection = mongo_client["global_news"]["gkg_records"]
        session = cluster.connect("global_news_analytics")

        insert_theme = session.prepare("""
            INSERT INTO daily_theme_metrics (
                news_date, theme, record_count
            )
            VALUES (?, ?, ?)
        """)

        insert_organization = session.prepare("""
            INSERT INTO daily_organization_metrics (
                news_date, organization, record_count
            )
            VALUES (?, ?, ?)
        """)

        dates = sorted(collection.distinct("date"))

        for date_str in dates:
            print(f"\nProcesando: {date_str}")

            theme_counts = Counter()
            organization_counts = Counter()

            records = collection.find(
                {"date": date_str},
                {"themes": 1, "organizations": 1}
            )

            for record in records:
                themes = {
                    theme.strip()
                    for theme in record.get("themes", [])
                    if isinstance(theme, str) and theme.strip()
                }

                organizations = {
                    org.strip()
                    for org in record.get("organizations", [])
                    if isinstance(org, str) and org.strip()
                }

                theme_counts.update(themes)
                organization_counts.update(organizations)

            news_date = datetime.strptime(
                date_str, "%Y%m%d"
            ).date()

            # Reemplazar las agregaciones del dia.
            # Evita conservar temas u organizaciones
            # que desaparezcan en un recalculo.
            session.execute(
                "DELETE FROM daily_theme_metrics WHERE news_date = %s",
                (news_date,)
            )

            session.execute(
                "DELETE FROM daily_organization_metrics WHERE news_date = %s",
                (news_date,)
            )

            for theme, count in theme_counts.items():
                session.execute(
                    insert_theme,
                    (news_date, theme, count)
                )

            for organization, count in organization_counts.items():
                session.execute(
                    insert_organization,
                    (news_date, organization, count)
                )

            print(f"Temas distintos: {len(theme_counts):,}")
            print(
                f"Organizaciones distintas: "
                f"{len(organization_counts):,}"
            )

            print("Top 5 temas:")
            for theme, count in theme_counts.most_common(5):
                print(f"  {theme}: {count:,}")

            print("Top 5 organizaciones:")
            for org, count in organization_counts.most_common(5):
                print(f"  {org}: {count:,}")

        print("\nAgregaciones de entidades completadas.")

    finally:
        cluster.shutdown()
        mongo_client.close()


if __name__ == "__main__":
    aggregate_entities()
