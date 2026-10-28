#inspeccionar el CSV sin descomprimirlo
import csv
import zipfile
from collections import Counter
from pathlib import Path

ZIP_PATH = Path("data/raw/20261027.gkg.csv.zip")


def inspect_file():
    with zipfile.ZipFile(ZIP_PATH, "r") as archive:
        csv_name = archive.namelist()[0]

        with archive.open(csv_name, "r") as binary_file:
            import io

            text_file = io.TextIOWrapper(
                binary_file,
                encoding="utf-8",
                errors="replace",
                newline="",
            )

            reader = csv.reader(text_file, delimiter="\t")

            header = next(reader, None)
            row_count = 0
            malformed_rows = 0
            dates = Counter()

            for row in reader:
                row_count += 1

                if header is None or len(row) != len(header):
                    malformed_rows += 1
                    continue

                if row and row[0]:
                    dates[row[0][:8]] += 1

    print(f"Archivo: {csv_name}")
    print(f"Columnas ({len(header) if header else 0}): {header}")
    print(f"Registros leídos: {row_count:,}")
    print(f"Filas con número incorrecto de columnas: {malformed_rows:,}")
    print(f"Fechas distintas: {len(dates)}")

    for date, count in dates.most_common(10):
        print(f"  {date}: {count:,} registros")


if __name__ == "__main__":
    inspect_file()
