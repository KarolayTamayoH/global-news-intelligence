ARG AIRFLOW_IMAGE=apache/airflow:2.11.1-python3.12
FROM ${AIRFLOW_IMAGE}
COPY requirements-pipeline.txt /tmp/requirements-pipeline.txt
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /tmp/requirements-pipeline.txt
ENV PYTHONPATH=/opt/gni
