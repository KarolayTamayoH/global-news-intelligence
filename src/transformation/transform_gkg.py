
import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path


def split_values(value):
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def transform_record(row, source_file, row_number):
    record_id = hashlib.sha256(
        f"{source_file}:{row_number}".encode("utf-8")
    ).hexdigest()

    return {
        "_id": record_id,
        "date": row["DATE"][:8],
        "num_articles": int(row["NUMARTS"]),
        "themes": split_values(row["THEMES"]),
        "persons": split_values(row["PERSONS"]),
        "organizations": split_values(row["ORGANIZATIONS"]),
        "sources": split_values(row["SOURCES"]),
        "source_urls": split_values(row["SOURCEURLS"]),
        "locations_raw": row["LOCATIONS"],
        "tone_raw": row["TONE"],
        "counts_raw": row["COUNTS"],
        "cameo_event_ids_raw": row["CAMEOEVENTIDS"],
        "source_file": source_file,
    }


def transform_file(zip_path):
    zip_path = Path(zip_path)

    if not zip_path.exists():
        raise FileNotFoundError(f"No existe: {zip_path}")

    date = zip_path.name[:8]
    output_path = Path("data/processed") / f"{date}.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    processed = 0
    rejected = 0

    with zipfile.ZipFile(zip_path) as archive:
        csv_name = archive.namelist()[0]

        with archive.open(csv_name) as binary_file:
            text_file = io.TextIOWrapper(
                binary_file,
                encoding="utf-8",
                errors="replace",
                newline="",
            )

            reader = csv.DictReader(text_file, delimiter="\t")

            with output_path.open("w", encoding="utf-8") as output:
                for row_number, row in enumerate(reader, start=1):
                    try:
                        record = transform_record(
                            row, zip_path.name, row_number
                        )
                        output.write(
                            json.dumps(record, ensure_ascii=False) + "\n"
                        )
                        processed += 1

                    except (ValueError, TypeError, KeyError):
                        rejected += 1

    print(f"Registros transformados: {processed:,}")
    print(f"Registros rechazados: {rejected:,}")
    print(f"Archivo generado: {output_path}")

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path", help="Ruta del archivo GKG ZIP")
    args = parser.parse_args()

    transform_file(args.zip_path)


