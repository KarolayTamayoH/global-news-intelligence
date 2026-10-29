#GKGRecord: representa un registro GKG con su identificador original de MongoDB.
# Theme: representa un código temático de GDELT.
# Organization: representa una entidad extraída del campo de organizaciones.
# HAS_THEME: conecta un registro con un tema.
# MENTIONS_ORG: conecta un registro con una organización.

import os
import argparse
from datetime import datetime, timezone
from time import perf_counter

from pymongo import MongoClient
from neo4j import GraphDatabase


MONGO_URI = "mongodb://localhost:27018/"
NEO4J_URI = "bolt://localhost:7688"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

BATCH_SIZE = 100


def save_batch(tx, records):
    query = """
    UNWIND $records AS record

    MERGE (r:GKGRecord {id: record.id})
    SET r.date = record.date,
        r.num_articles = record.num_articles

    WITH r, record

    FOREACH (theme IN record.themes |
        MERGE (t:Theme {name: theme})
        MERGE (r)-[:HAS_THEME]->(t)
    )

    FOREACH (org IN record.organizations |
        MERGE (o:Organization {name: org})
        MERGE (r)-[:MENTIONS_ORG]->(o)
    )
    """

    tx.run(query, records=records).consume()


def load_neo4j(target_date, limit=None):
    if not NEO4J_PASSWORD:
        raise ValueError(
            "Configura la variable de entorno NEO4J_PASSWORD"
        )

    if limit is not None and limit <= 0:
        raise ValueError("--limit debe ser mayor que cero")

    # Validar el formato de la fecha
    datetime.strptime(target_date, "%Y%m%d")

    mongo_client = MongoClient(MONGO_URI)
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    try:
        driver.verify_connectivity()

        database = mongo_client["global_news"]
        collection = database["gkg_records"]
        history = database["neo4j_ingestion_history"]

        # Evitar repetir una carga completa
        if limit is None:
            previous = history.find_one({"_id": target_date})

            if previous and previous.get("status") == "completed":
                print(f"Fecha ya procesada en Neo4j: {target_date}")
                return

        start = perf_counter()
        started_at = datetime.now(timezone.utc)

        cursor = collection.find(
            {"date": target_date},
            {
                "_id": 1,
                "date": 1,
                "num_articles": 1,
                "themes": 1,
                "organizations": 1
            }
        ).sort("_id", 1)

        # Aplicar el limite solo si es una prueba
        if limit is not None:
            cursor = cursor.limit(limit)

        batch = []
        processed = 0

        with driver.session(database="neo4j") as session:
            for doc in cursor:
                record = {
                    "id": str(doc["_id"]),
                    "date": doc.get("date", ""),
                    "num_articles": doc.get("num_articles", 0),
                    "themes": sorted(set(
                        theme.strip()
                        for theme in doc.get("themes", [])[:10]
                        if isinstance(theme, str) and theme.strip()
                    )),
                    "organizations": sorted(set(
                        org.strip()
                        for org in doc.get("organizations", [])[:10]
                        if isinstance(org, str) and org.strip()
                    ))
                }

                batch.append(record)

                if len(batch) == BATCH_SIZE:
                    session.execute_write(save_batch, batch)
                    processed += len(batch)

                    print(f"Registros procesados: {processed}")
                    batch = []

            # Guardar el ultimo lote incompleto
            if batch:
                session.execute_write(save_batch, batch)
                processed += len(batch)

        print(f"\nCarga completada: {processed} registros")

        # Registrar solo las cargas completas
        if limit is None:
            expected = collection.count_documents(
                {"date": target_date}
            )

            if processed != expected:
                raise ValueError(
                    f"Registros incompletos: {processed}/{expected}"
                )

            if expected == 0:
                # Verificar los registros realmente almacenados en Neo4j
                with driver.session(database="neo4j") as session:
                    result = session.run(
                        """
                        MATCH (r:GKGRecord {date: $date})
                        RETURN count(r) AS total
                        """,
                        date=target_date
                    ).single()

                    stored = result["total"]

                if stored != expected:
                    raise ValueError(
                        f"Neo4j contiene {stored} registros, "
                        f"pero MongoDB contiene {expected}"
                    )

                print(f"Verificacion Neo4j: {stored:,}/{expected:,}")
                raise ValueError(
                    f"No hay registros para la fecha {target_date}"
                )

            history.update_one(
                {"_id": target_date},
                {
                    "$set": {
                        "status": "completed",
                        "records": processed,
                        "duration_seconds": round(
                            perf_counter() - start, 2
                        ),
                        "started_at": started_at,
                        "completed_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )

            print("Historial de Neo4j actualizado")

        else:
            print(
                "Carga de prueba: "
                "no se marca la fecha como completada"
            )

    finally:
        driver.close()
        mongo_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Carga registros GKG desde MongoDB hacia Neo4j"
    )

    parser.add_argument(
        "--date",
        required=True,
        help="Fecha en formato YYYYMMDD"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limite opcional para pruebas"
    )

    args = parser.parse_args()

    load_neo4j(args.date, args.limit)
