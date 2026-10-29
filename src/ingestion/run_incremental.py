
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.ingestion.check_gdelt_index import get_available_files
from src.ingestion.download_gdelt import download_file
from src.ingestion.load_mongodb import load_mongodb
from src.transformation.transform_gkg import transform_file
from src.validation.validate_gkg import validate_gkg

MONGO_URI = "mongodb://localhost:27018/"
DATABASE = "global_news"


def run_incremental(days=7):
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    try:
        client.admin.command("ping")
        history = client[DATABASE]["ingestion_history"]

        available_files = get_available_files()

        if not available_files:
            raise RuntimeError("No se encontraron archivos GKG.")

        selected_files = list(reversed(available_files[:days]))

        print(f"Archivos seleccionados: {len(selected_files)}")

        for filename in selected_files:
            previous = history.find_one({"_id": filename})

            if previous and previous.get("status") == "completed":
                print(f"Ya procesado, se omite: {filename}")
                continue

            print(f"\nProcesando: {filename}")
            start = perf_counter()

            history.update_one(
                {"_id": filename},
                {
                    "$set": {
                        "date": filename[:8],
                        "status": "processing",
                        "started_at": datetime.now(timezone.utc),
                    },
                    "$unset": {"error": ""},
                },
                upsert=True,
            )

            try:
                # 1. Descargar y comprobar la integridad del ZIP.
                zip_path = download_file(filename)

                # 2. Validar el esquema y los registros.
                validation = validate_gkg(zip_path)

                # 3. Transformar a JSONL.
                output_path = transform_file(zip_path)

                # 4. Cargar en MongoDB.
                stats = load_mongodb(output_path)

                if stats["processed"] != validation["total"]:
                  raise ValueError(
                      "La cantidad de documentos cargados no coincide "
                      "con los registros validados"
                  )

                duration = round(perf_counter() - start, 2)

                history.update_one(
                    {"_id": filename},
                    {
                        "$set": {
                            "status": "completed",
                            "records": stats["processed"],
                            "inserted": stats["inserted"],
                            "existing": stats["existing"],
                            "duration_seconds": duration,
                            "completed_at": datetime.now(timezone.utc),
                        }
                    },
                )

                print(f"Completado: {filename}")
                print(f"Duracion: {duration} segundos")

            except Exception as error:
                duration = round(perf_counter() - start, 2)

                history.update_one(
                    {"_id": filename},
                    {
                        "$set": {
                            "status": "failed",
                            "error": str(error),
                            "duration_seconds": duration,
                            "failed_at": datetime.now(timezone.utc),
                        }
                    },
                )

                print(f"Error en {filename}: {error}")
                raise

    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Cantidad de archivos diarios recientes",
    )

    args = parser.parse_args()

    if args.days < 1:
        parser.error("--days debe ser mayor que cero")

    run_incremental(days=args.days)

