"""Verificar la aplicacion Streamlit contra las tres bases locales activas."""
import argparse
import json
from datetime import datetime
from pathlib import Path

import streamlit as st
from streamlit.testing.v1 import AppTest

from src.config import ROOT
from src.validation.validate_gkg import validate_target_date


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', default='20261027')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/dashboard_verification.json')
    args = parser.parse_args()
    validate_target_date(args.date)
    st.cache_data.clear()
    st.cache_resource.clear()
    app = AppTest.from_file(str(ROOT / 'dashboard/app.py')).run(timeout=120)
    selected = datetime.strptime(args.date, '%Y%m%d').date()
    app.selectbox(key='analysis_date').select(selected).run(timeout=120)
    if app.exception or app.warning or app.error:
        raise ValueError('La aplicacion presenta errores o fuentes no disponibles')
    if len(app.tabs) != 3:
        raise ValueError('Faltan vistas multimodelo')
    metrics = {item.label: item.value for item in app.metric}
    for label in ['Registros encontrados en MongoDB', 'Registros en Neo4j']:
        if int(metrics.get(label, '0').replace(',', '')) <= 0:
            raise ValueError(f'Faltan datos: {label}')
    if not app.json or len(app.dataframe) < 3:
        raise ValueError('Falta el documento o las tablas de analisis')
    result = {'status': 'verified', 'mode': 'local', 'date': args.date,
              'sources': ['Cassandra', 'MongoDB', 'Neo4j'],
              'tabs': [item.label for item in app.tabs], 'metrics': metrics,
              'warnings': 0, 'exceptions': 0, 'sample_document_visible': True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
