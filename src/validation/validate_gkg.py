#La validación deberá comprobar que el archivo contiene las 11 columnas esperadas, que las fechas tienen el formato correcto y que corresponden al día del archivo.

import csv
import io
import re
import zipfile
from pathlib import Path
from datetime import datetime

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


def validate_target_date(value):
    """Validate a daily partition without accepting abbreviated dates."""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{8}", value):
        raise ValueError("La fecha debe tener formato YYYYMMDD")
    datetime.strptime(value, "%Y%m%d")
    return value


def validate_gkg_archive(zip_source, expected_date):
    """Shared contract for a ZIP path or a seekable binary stream."""
    validate_target_date(expected_date)

    total = 0
    invalid = 0

    with zipfile.ZipFile(zip_source) as archive:
        expected_csv = f"{expected_date}.gkg.csv"
        if archive.namelist() != [expected_csv]:
            raise ValueError(f"Se esperaba un unico archivo {expected_csv}")
        if archive.testzip() is not None:
            raise ValueError("Archivo ZIP corrupto")

        csv_name = expected_csv

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

                try:
                    if len(row[0]) == 8:
                        validate_target_date(row[0])
                    elif re.fullmatch(r"[0-9]{14}", row[0]):
                        datetime.strptime(row[0], "%Y%m%d%H%M%S")
                    else:
                        raise ValueError("Fecha GKG invalida")
                except ValueError:
                    invalid += 1
                    continue

                if row[0][:8] != expected_date:
                    invalid += 1
                    continue

                if not re.fullmatch(r"[0-9]+", row[1]):
                    invalid += 1

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


def validate_gkg(zip_path):
    zip_path = Path(zip_path)
    result = validate_gkg_archive(zip_path, zip_path.name[:8])
    print(f"Archivo validado: {zip_path.name}")
    print(f"Registros: {result['total']:,}")
    print(f"Registros invalidos: {result['invalid']:,}")
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path")
    args = parser.parse_args()

    validate_gkg(args.zip_path)
