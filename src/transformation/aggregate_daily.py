#Consulta las fechas disponibles en MongoDB.
#Recorre los documentos correspondientes a cada fecha sin cargarlos todos simultáneamente en memoria.
#Cuenta los registros GKG y los temas distintos.
#Extrae el primer valor numérico de tone_raw para calcular el tono promedio.
#Inserta las métricas en Cassandra.


from datetime import datetime

from pymongo import MongoClient
from cassandra.cluster import Cluster


from src.config import MONGO_URI, MONGO_DATABASE, CASSANDRA_HOST, CASSANDRA_PORT, CASSANDRA_KEYSPACE
from src.validation.validate_gkg import validate_target_date


def aggregate_daily(target_date=None):
    if target_date is not None:
        validate_target_date(target_date)
    mongo_client = MongoClient(MONGO_URI)
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)

    try:
        mongo_collection = mongo_client[MONGO_DATABASE]["gkg_records"]
        session = cluster.connect(CASSANDRA_KEYSPACE)
        if target_date and mongo_collection.count_documents({"date": target_date}) == 0:
            raise ValueError(f"No hay registros para la fecha {target_date}")


        insert_query = session.prepare("""
            INSERT INTO daily_news_metrics (
                metric_group,
                news_date,
                total_records,
                unique_themes,
                average_tone
            )
            VALUES (?, ?, ?, ?, ?)
        """)

        dates = [target_date] if target_date else sorted(mongo_collection.distinct("date"))

        for date_str in dates:
            print(f"\nProcesando fecha: {date_str}")

            records = mongo_collection.find(
                {"date": date_str},
                {"themes": 1, "tone_raw": 1}
            )

            total_records = 0
            unique_themes = set()
            tone_sum = 0.0
            tone_count = 0

            for record in records:
                total_records += 1

                for theme in record.get("themes", []):
                    unique_themes.add(theme)

                tone_raw = record.get("tone_raw", "")

                if tone_raw:
                    try:
                        tone = float(tone_raw.split(",")[0])
                        tone_sum += tone
                        tone_count += 1
                    except (ValueError, TypeError):
                        pass

            average_tone = (
                tone_sum / tone_count
                if tone_count > 0
                else None
            )

            news_date = datetime.strptime(
                date_str, "%Y%m%d"
            ).date()

            session.execute(
                insert_query,
                (
                    "global",
                    news_date,
                    total_records,
                    len(unique_themes),
                    average_tone
                )
            )

            print(f"Registros: {total_records:,}")
            print(f"Temas distintos: {len(unique_themes):,}")
            print(f"Tono promedio: {average_tone}")

        print("\nAgregaciones diarias completadas.")

    finally:
        cluster.shutdown()
        mongo_client.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Particion YYYYMMDD; por defecto todas las fechas")
    args = parser.parse_args()
    aggregate_daily(args.date)
