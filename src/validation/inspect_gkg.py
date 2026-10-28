import csv
import zipfile
from collections import Counter
from pathlib import Path

ZIP_PATH = Path("data/raw/gdelt_sample.zip")
REPORT_PATH = Path("docs/data_quality.txt")


def inspect_file():
    total = 0
    malformed = 0
    empty_values = Counter()
    dates = Counter()

    with zipfile.ZipFile(ZIP_PATH) as archive:
        filename = archive.namelist()[0]

        with archive.open(filename) as file:
            reader = csv.reader(
                (line.decode("utf-8", errors="replace") for line in file),
                delimiter="\t",
            )

            header = next(reader)

            for row in reader:
                total += 1

                if len(row) != len(header):
                    malformed += 1
                    continue

                dates[row[0]] += 1

                for name, value in zip(header, row):
                    if not value.strip():
                        empty_values[name] += 1

    report = [
        "INFORME DE CALIDAD GDELT GKG",
        f"Archivo: {ZIP_PATH}",
        f"Columnas: {len(header)}",
        f"Registros leidos: {total}",
        f"Registros mal formados: {malformed}",
        f"Fechas distintas: {len(dates)}",
        "",
        "Registros por fecha:",
        *[f"{date}: {count}" for date, count in sorted(dates.items())],
        "",
        "Campos vacios por columna:",
        *[f"{name}: {count}" for name, count in empty_values.items()],
    ]

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\n".join(report))
    print(f"\nInforme guardado en: {REPORT_PATH}")


if __name__ == "__main__":
    inspect_file()