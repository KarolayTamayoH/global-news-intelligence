
import argparse
import sys
from pathlib import Path

from pymongo import MongoClient

# Permitir importar modulos desde la raiz del proyecto.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.ingestion.check_gdelt_index import get_available_files
from src.ingestion.download_gdelt import download_file
from src.ingestion.load_mongodb import load_mongodb
from src.transformation.transform_gkg import transform_file


MONGO_URI = "mongodb://localhost:27018/"
DATABASE = "global_news"

RAW_DIR = ROOT / "data/raw"


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
            raise RuntimeError(
                "No se encontraron archivos en GDELT."
            )

        # Seleccionar los archivos diarios mas recientes.
        selected_files = available_files[:days]

        # Procesar en orden cronologico.
        selected_files.reverse()

        print(f"Archivos seleccionados: {len(selected_files)}")

        for filename in selected_files:
            previous = history.find_one({"_id": filename})

            if previous and previous.get("status") == "completed":
                print(f"Ya procesado, se omite: {filename}")
                continue

            print(f"\nProcesando: {filename}")

            try:
                # 1. Descargar.
                download_file(filename)

                zip_path = RAW_DIR / filename

                # 2. Transformar.
                output_path = transform_file(zip_path)

                # 3. Cargar MongoDB.
                load_mongodb(output_path)

                # 4. Registrar archivo completado.
                history.update_one(
                    {"_id": filename},
                    {
                        "$set": {
                            "date": filename[:8],
                            "status": "completed",
                        }
                    },
                    upsert=True,
                )

                print(f"Completado: {filename}")

            except Exception as error:
                history.update_one(
                    {"_id": filename},
                    {
                        "$set": {
                            "date": filename[:8],
                            "status": "failed",
                            "error": str(error),
                        }
                    },
                    upsert=True,
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
