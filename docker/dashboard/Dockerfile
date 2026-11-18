FROM python:3.11-slim

WORKDIR /opt/gni

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY dashboard /opt/gni/dashboard
COPY src /opt/gni/src

ENV PYTHONPATH=/opt/gni
EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--browser.gatherUsageStats=false"]
