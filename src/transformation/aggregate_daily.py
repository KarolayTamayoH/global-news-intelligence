#Consulta las fechas disponibles en MongoDB.
#Recorre los documentos correspondientes a cada fecha sin cargarlos todos simultáneamente en memoria.
#Cuenta los registros GKG y los temas distintos.
#Extrae el primer valor numérico de tone_raw para calcular el tono promedio.
#Inserta las métricas en Cassandra.


from datetime import datetime

from pymongo import MongoClient
from cassandra.cluster import Cluster


MONGO_URI = "mongodb://localhost:27018/"
CASSANDRA_HOST = "127.0.0.1"
CASSANDRA_PORT = 9043


def aggregate_daily():
    mongo_client = MongoClient(MONGO_URI)
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)

    try:
        mongo_collection = mongo_client["global_news"]["gkg_records"]
        session = cluster.connect("global_news_analytics")

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

        dates = sorted(mongo_collection.distinct("date"))

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
    aggregate_daily()
