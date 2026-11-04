
import io
import logging
from datetime import timedelta
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

import pendulum
from airflow.decorators import dag, task
from src.validation.validate_gkg import validate_gkg_archive, validate_target_date


GDELT_BASE_URL = "https://data.gdeltproject.org/gkg"


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
        # Fecha manual o dia anterior a la fecha logica de la ejecucion (UTC)
        conf = context["dag_run"].conf or {}
        target_date = conf.get("target_date")

        if target_date is None:
            logical_date = context.get("logical_date")
            if logical_date is None:
                raise ValueError("Indica target_date cuando no haya fecha logica")
            target_date = logical_date.in_timezone("UTC").subtract(days=1).format("YYYYMMDD")

        validate_target_date(target_date)

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

        validation = validate_gkg_archive(io.BytesIO(zip_bytes), target_date)
        valid_rows = validation["total"]

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
