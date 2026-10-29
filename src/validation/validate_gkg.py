#La validación deberá comprobar que el archivo contiene las 11 columnas esperadas, que las fechas tienen el formato correcto y que corresponden al día del archivo.

import csv
import io
import re
import zipfile
from pathlib import Path

EXPECTED_COLUMNS = [
    "DATE",
    "NUMARTS",
    "COUNTS",
    "THEMES",
    "LOCATIONS",
    "PERSONS",
    "ORGANIZATIONS",
    "TONE",
    "CAMEOEVENTIDS",
    "SOURCES",
    "SOURCEURLS",
]


def validate_gkg(zip_path):
    zip_path = Path(zip_path)
    expected_date = zip_path.name[:8]

    if not re.fullmatch(r"\d{8}", expected_date):
        raise ValueError("Fecha invalida en el nombre del archivo")

    total = 0
    invalid = 0

    with zipfile.ZipFile(zip_path) as archive:
        csv_name = archive.namelist()[0]

        with archive.open(csv_name) as binary_file:
            text_file = io.TextIOWrapper(
                binary_file,
                encoding="utf-8",
                errors="replace",
                newline="",
            )

            reader = csv.reader(text_file, delimiter="\t")
            header = next(reader, None)

            if header != EXPECTED_COLUMNS:
                raise ValueError(
                    f"Esquema inesperado: {header}"
                )

            for row in reader:
                total += 1

                if len(row) != len(EXPECTED_COLUMNS):
                    invalid += 1
                    continue

                if row[0][:8] != expected_date:
                    invalid += 1
                    continue

                if not row[1].isdigit():
                    invalid += 1

    print(f"Archivo validado: {zip_path.name}")
    print(f"Registros: {total:,}")
    print(f"Registros invalidos: {invalid:,}")

    if total == 0:
        raise ValueError("El archivo no contiene registros")

    if invalid > 0:
        raise ValueError(
            f"Se encontraron {invalid} registros invalidos"
        )

    return {
        "total": total,
        "invalid": invalid,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path")
    args = parser.parse_args()

    validate_gkg(args.zip_path)
