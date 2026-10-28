
import argparse
import json
from pathlib import Path

from pymongo import MongoClient, UpdateOne

MONGO_URI = "mongodb://localhost:27018/"
DATABASE = "global_news"
COLLECTION = "gkg_records"
BATCH_SIZE = 1000


def load_mongodb(input_path):
    input_path = Path(input_path)

    if not input_path.is_file():
        raise FileNotFoundError(f"No existe: {input_path}")

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        collection = client[DATABASE][COLLECTION]

        operations = []
        processed = 0
        inserted = 0
        existing = 0

        def save_batch():
            nonlocal operations, processed, inserted, existing

            if not operations:
                return

            result = collection.bulk_write(
                operations, ordered=False
            )

            processed += len(operations)
            inserted += result.upserted_count
            existing += result.matched_count
            operations = []

        with input_path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                record = json.loads(line)

                operations.append(
                    UpdateOne(
                        {"_id": record["_id"]},
                        {"$setOnInsert": record},
                        upsert=True,
                    )
                )

                if len(operations) >= BATCH_SIZE:
                    save_batch()

        save_batch()

        print(f"Archivo: {input_path.name}")
        print(f"Registros procesados: {processed:,}")
        print(f"Documentos nuevos: {inserted:,}")
        print(f"Documentos existentes: {existing:,}")
        print(f"Total en MongoDB: {collection.count_documents({}):,}")

    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_path",
        help="Ruta del archivo JSONL transformado"
    )
    args = parser.parse_args()

    load_mongodb(args.input_path)

