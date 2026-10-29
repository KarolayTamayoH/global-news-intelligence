
import io
import csv
import logging
import zipfile
from datetime import timedelta
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

import pendulum
from airflow.decorators import dag, task


GDELT_BASE_URL = "https://data.gdeltproject.org/gkg"
EXPECTED_COLUMNS = 11


@dag(
    dag_id="global_news_ingestion",
    description="Descarga y validacion diaria de GDELT GKG",
    schedule=None,  # Primero ejecutaremos manualmente
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["gdelt", "big-data", "global-news"],
)
def global_news_ingestion():

    @task
    def check_availability(**context):
        # Fecha indicada manualmente o dia anterior en UTC
        conf = context["dag_run"].conf or {}
        target_date = conf.get("target_date")

        if not target_date:
            target_date = (
                pendulum.now("UTC").subtract(days=1).format("YYYYMMDD")
            )

        # Validar formato y fecha real
        pendulum.from_format(
            target_date, "YYYYMMDD", tz="UTC", strict=True
        )

        filename = f"{target_date}.gkg.csv.zip"
        url = f"{GDELT_BASE_URL}/{filename}"

        try:
            with urlopen(url, timeout=30) as response:
                # Solo leemos un fragmento para verificar acceso
                response.read(1024)
        except (HTTPError, URLError) as error:
            raise RuntimeError(
                f"No se pudo acceder a {url}: {error}"
            ) from error

        logging.info("Archivo GDELT disponible: %s", url)

        return {
            "date": target_date,
            "url": url,
            "filename": filename,
        }

    @task
    def download_and_validate(file_info):
        url = file_info["url"]
        target_date = file_info["date"]

        logging.info("Descargando %s", url)

        with urlopen(url, timeout=180) as response:
            zip_bytes = response.read()

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            bad_file = archive.testzip()

            if bad_file is not None:
                raise ValueError(
                    f"Archivo ZIP corrupto: {bad_file}"
                )

            csv_files = [
                name for name in archive.namelist()
                if name.lower().endswith(".csv")
            ]

            if len(csv_files) != 1:
                raise ValueError(
                    "Se esperaba un unico archivo CSV dentro del ZIP"
                )

            valid_rows = 0

            with archive.open(csv_files[0]) as raw_file:
                text_file = io.TextIOWrapper(
                    raw_file, encoding="utf-8", errors="replace"
                )

                reader = csv.reader(
                    text_file,
                    delimiter="\t"
                )

                for row in reader:
                    if len(row) != EXPECTED_COLUMNS:
                        raise ValueError(
                            f"Fila con {len(row)} columnas; "
                            f"se esperaban {EXPECTED_COLUMNS}"
                        )

                    if not row[0].startswith(target_date):
                        raise ValueError(
                            "Fecha GKG diferente de la solicitada"
                        )

                    if not row[1].isdigit():
                        raise ValueError(
                            "NUMARTS no es numerico"
                        )

                    valid_rows += 1

        if valid_rows == 0:
            raise ValueError("El archivo no contiene registros")

        logging.info(
            "Validacion completada: %s registros GKG",
            valid_rows
        )

        return {
            "date": target_date,
            "records": valid_rows,
            "status": "validated",
        }

    file_info = check_availability()
    download_and_validate(file_info)


global_news_ingestion()
