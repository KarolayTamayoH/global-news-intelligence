"""Dashboard local: indicadores Cassandra, documentos MongoDB y relaciones Neo4j."""

import streamlit as st
import pandas as pd
import plotly.express as px

from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from src.transformation.aggregate_snapshot import active_entity_metrics
from pymongo import MongoClient
from neo4j import GraphDatabase
from datetime import date

from dashboard import queries
from dashboard.graph import graph_figure
from src.config import MONGO_URI, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from src.config import CASSANDRA_HOST, CASSANDRA_PORT, CASSANDRA_KEYSPACE


# Configuracion de pagina
st.set_page_config(
    page_title="Global News Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Estilos del dashboard

st.markdown("""
<style>
    .block-container {
        max-width: 1120px;
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
    }

    div[data-testid="stMetric"] {
        background-color: #161e2d;
        border: 1px solid #293548;
        border-radius: 12px;
        padding: 14px 18px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #a9b8cd;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #f4f7fb;
    }

    h1 {
        font-size: 2rem !important;
        letter-spacing: -0.5px;
    }

    h2, h3 {
        font-size: 1.25rem !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.65rem;
    }
</style>
""", unsafe_allow_html=True)



# Conexion a Cassandra
@st.cache_resource
def get_cassandra_session():
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
    try:
        session = cluster.connect(CASSANDRA_KEYSPACE)
        session.default_consistency_level = ConsistencyLevel.LOCAL_QUORUM
        return session
    except Exception:
        cluster.shutdown()
        raise


# Datos diarios
@st.cache_data(ttl=60)
def get_daily_metrics():
    session = get_cassandra_session()

    rows = session.execute("""
    SELECT news_date,
           total_records,
           unique_themes,
           average_tone
    FROM daily_news_metrics
    WHERE metric_group = 'global'
    """)

    data = [
        {
            "fecha": row.news_date.date(),
            "registros": row.total_records,
            "temas_unicos": row.unique_themes,
            "tono_promedio": row.average_tone
        }
        for row in rows
    ]

    df = pd.DataFrame(
    data,
    columns=[
        "fecha",
        "registros",
        "temas_unicos",
        "tono_promedio"
    ]
)

    if not df.empty:
        df = df.sort_values("fecha").reset_index(drop=True)
        previous = df["registros"].shift(1)
        df["variacion_pct"] = (df["registros"] - previous) / previous.where(previous > 0) * 100

    return df


# Consultar los 10 temas mas frecuentes de una fecha
@st.cache_data(ttl=60)
def get_top_themes(target_date):
    session = get_cassandra_session()

    rows = active_entity_metrics(session, target_date, 'theme')

    data = [
        {
            "tema": row.theme,
            "registros": row.record_count
        }
        for row in rows
    ]

    df = pd.DataFrame(data, columns=["tema", "registros"])

    if not df.empty:
        df = df.sort_values(
            "registros",
            ascending=False
        ).head(10)

    return df


# KPI 6: Top 10 entidades organizacionales
@st.cache_data(ttl=60)
def get_top_organizations(target_date):
    session = get_cassandra_session()

    rows = active_entity_metrics(session, target_date, 'organization')

    data = [
        {
            "organizacion": row.organization,
            "registros": row.record_count
        }
        for row in rows
    ]

    df = pd.DataFrame(
        data,
        columns=["organizacion", "registros"]
    )

    if not df.empty:
        df = (
            df.sort_values(
                "registros",
                ascending=False
            )
            .head(10)
            .copy()
        )

    return df

def render_indicators(df, selected_date):
    # Metricas principales
    total = int(df["registros"].sum())
    latest = int(df.iloc[-1]["registros"])
    latest_date = df.iloc[-1]["fecha"]
    variation = df.iloc[-1]["variacion_pct"]

    st.subheader("Panorama general")

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.metric(
            "Registros analizados",
            f"{total:,}"
        )

    with col2:
        st.metric(
            "Registros del ultimo dia",
            f"{latest:,}",
            help=f"Fecha: {latest_date}"
        )

    with col3:
        if pd.notna(variation):
            st.metric(
                "Variacion diaria",
                f"{variation:+.2f}%",
                delta=f"{variation:+.2f}%"
            )
        else:
            st.metric("Variacion diaria", "N/D")

    st.write("")

    # Grafico de evolucion
    st.subheader("Evolucion temporal")

    fig = px.line(
        df,
        x="fecha",
        y="registros",
        markers=True
    )

    fig.update_traces(
        line=dict(color="#54b6ff", width=3),
        marker=dict(size=9)
    )

    fig.update_layout(
        template="plotly_dark",
        height=390,
        margin=dict(l=20, r=20, t=25, b=20),
        xaxis_title="Fecha",
        yaxis_title="Registros GKG",
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    fig.update_xaxes(dtick=86400000, tickformat="%d/%m/%Y")
    fig.update_yaxes(rangemode="tozero", tickformat=",d")

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    # KPI 3: Top 10 temas
    st.subheader("Top 10 temas mas mencionados")

    top_themes = get_top_themes(selected_date)

    if top_themes.empty:
        st.info("No hay datos tematicos para esta fecha.")
    else:
        fig_themes = px.bar(
            top_themes,
            x="registros",
            y="tema",
            orientation="h",
            text="registros"
        )

        fig_themes.update_traces(
            marker_color="#54b6ff",
            textposition="outside"
        )

        fig_themes.update_layout(
            template="plotly_dark",
            height=480,
            margin=dict(l=20, r=80, t=20, b=20),
            xaxis_title="Registros GKG",
            yaxis_title="",
            yaxis=dict(
                categoryorder="total ascending",
                automargin=True
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.caption(
            f"Fecha analizada: {selected_date} | "
            "Un registro puede contener varios temas."
        )

        st.plotly_chart(
            fig_themes,
            width="stretch",
            config={"displayModeBar": False}
        )

    # KPI 4 y KPI 5
    st.subheader("Diversidad tematica y tono informativo")

    latest_themes = int(df.iloc[-1]["temas_unicos"])
    latest_tone = df.iloc[-1]["tono_promedio"]

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.metric(
            "Temas distintos del ultimo dia",
            f"{latest_themes:,}"
        )

        fig_diversity = px.line(
            df,
            x="fecha",
            y="temas_unicos",
            markers=True
        )

        fig_diversity.update_traces(
            line=dict(color="#a78bfa", width=3),
            marker=dict(size=8)
        )

        fig_diversity.update_layout(
            template="plotly_dark",
            height=340,
            margin=dict(l=10, r=10, t=20, b=20),
            xaxis_title="Fecha",
            yaxis_title="Temas distintos",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        fig_diversity.update_xaxes(dtick=86400000, tickformat="%d/%m/%Y")
        fig_diversity.update_yaxes(rangemode="tozero", tickformat=",d")

        st.plotly_chart(
            fig_diversity,
            width="stretch",
            config={"displayModeBar": False}
        )

    with col2:
        st.metric(
            "Tono promedio del ultimo dia",
            f"{latest_tone:+.2f}" if pd.notna(latest_tone) else "N/D"
        )

        fig_tone = px.line(
            df,
            x="fecha",
            y="tono_promedio",
            markers=True
        )

        fig_tone.update_traces(
            line=dict(color="#f59e0b", width=3),
            marker=dict(size=8)
        )

        fig_tone.add_hline(
            y=0,
            line_dash="dash",
            line_color="#94a3b8"
        )

        fig_tone.update_layout(
            template="plotly_dark",
            height=340,
            margin=dict(l=10, r=10, t=20, b=20),
            xaxis_title="Fecha",
            yaxis_title="Tono promedio GDELT",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        fig_tone.update_xaxes(dtick=86400000, tickformat="%d/%m/%Y")

        st.plotly_chart(
            fig_tone,
            width="stretch",
            config={"displayModeBar": False}
        )

    st.caption(
        "La diversidad corresponde a codigos tematicos distintos. "
        "El tono es el promedio de los valores disponibles en GDELT GKG."
    )


    # KPI 6: Entidades organizacionales
    st.subheader("Top 10 entidades organizacionales")

    top_orgs = get_top_organizations(selected_date)

    if top_orgs.empty:
        st.info(
            "No hay datos de entidades para esta fecha."
        )
    else:
        fig_orgs = px.bar(
            top_orgs,
            x="registros",
            y="organizacion",
            orientation="h",
            text="registros"
        )

        fig_orgs.update_traces(
            marker_color="#34d399",
            textposition="outside"
        )

        fig_orgs.update_layout(
            template="plotly_dark",
            height=470,
            margin=dict(l=20, r=85, t=20, b=20),
            xaxis_title="Registros GKG",
            yaxis_title="",
            yaxis=dict(
                categoryorder="total ascending",
                automargin=True
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.caption(
            f"Fecha analizada: {selected_date} | "
            "Entidades extraidas del campo de organizaciones "
            "de GDELT."
        )

        st.plotly_chart(
            fig_orgs,
            width="stretch",
            config={"displayModeBar": False}
        )


    # Tabla de datos
    with st.expander("Ver datos diarios"):
        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            column_config={
                "fecha": st.column_config.DateColumn(
                    "Fecha",
                    format="DD/MM/YYYY"
                ),
                "registros": st.column_config.NumberColumn(
                    "Registros GKG",
                    format="%d"
                ),
                "variacion_pct": st.column_config.NumberColumn(
                    "Variacion (%)",
                    format="%.2f%%"
                )
            }
        )

    st.caption(
        "Fuente: GDELT GKG | "
        "Procesamiento: MongoDB y Cassandra | "
        "Los registros GKG no equivalen a articulos unicos."
    )

@st.cache_resource
def get_mongo_client():
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)


@st.cache_resource
def get_neo4j_driver():
    if not NEO4J_PASSWORD:
        raise ValueError('Falta configurar NEO4J_PASSWORD')
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD),
                                  connection_timeout=5)
    try:
        driver.verify_connectivity()
    except Exception:
        driver.close()
        raise
    return driver


@st.cache_data(ttl=60)
def document_dates():
    return queries.get_document_dates(get_mongo_client())


@st.cache_data(ttl=60)
def documents(target_date, theme, organization, page, page_size):
    return queries.search_documents(get_mongo_client(), target_date, theme, organization, page, page_size)


@st.cache_data(ttl=60)
def graph_counts(target_date):
    return queries.get_graph_counts(get_neo4j_driver(), target_date)


@st.cache_data(ttl=60)
def graph_sample(target_date, entity_type, entity_name, record_limit):
    return queries.get_graph_sample(get_neo4j_driver(), target_date, entity_type, entity_name, record_limit)


def render_documents(target_date):
    st.subheader('Explorador documental')
    st.caption(f'Fuente: MongoDB · Fecha {target_date[6:8]}/{target_date[4:6]}/{target_date[:4]} · Registros normalizados.')
    with st.form('document_filters'):
        col1, col2 = st.columns(2)
        theme = col1.text_input('Tema: código exacto', max_chars=128)
        organization = col2.text_input('Organización: contiene', max_chars=128)
        col1, col2 = st.columns(2)
        page = col1.number_input('Página', min_value=1, value=1, step=1)
        page_size = col2.selectbox('Registros por página', [20, 50, 100])
        st.form_submit_button('Consultar documentos')
    result = documents(target_date, theme, organization, int(page), page_size)
    st.metric('Registros encontrados en MongoDB', f"{result['total']:,}")
    items = result['documents']
    if not items:
        st.info('No hay registros en esta página para los filtros seleccionados.')
        return
    st.dataframe(pd.DataFrame([{
        'Identificador': item['_id'][:16], 'Artículos asociados': item.get('num_articles', 0),
        'Temas': '; '.join(item.get('themes', []))[:250],
        'Organizaciones': '; '.join(item.get('organizations', []))[:250],
    } for item in items]), width='stretch', hide_index=True, height=360,
        column_config={
            'Identificador': st.column_config.TextColumn(width='small'),
            'Artículos asociados': st.column_config.NumberColumn(width='small'),
            'Temas': st.column_config.TextColumn(width='medium'),
            'Organizaciones': st.column_config.TextColumn(width='medium'),
        })
    selected = st.selectbox('Ver documento completo', [item['_id'] for item in items],
                            format_func=lambda value: value[:20], key='document_id')
    st.json(next(item for item in items if item['_id'] == selected), expanded=False)
    st.caption('Un registro GKG puede agrupar varios artículos; el conteo no representa noticias únicas.')


def render_graph(target_date):
    st.subheader('Explorador de relaciones')
    st.caption(f'Fuente: Neo4j · Fecha {target_date[6:8]}/{target_date[4:6]}/{target_date[:4]} · Registros, temas y organizaciones.')
    counts = graph_counts(target_date)
    columns = st.columns(3)
    for column, label, key in zip(columns, ['Registros en Neo4j', 'Relaciones con temas',
                                          'Relaciones con organizaciones'],
                                  ['records', 'themes', 'organizations']):
        column.metric(label, f'{counts[key]:,}')
    with st.form('graph_filters'):
        col1, col2, col3 = st.columns([1, 2, 1])
        entity_type = col1.selectbox('Tipo de entidad', ['Theme', 'Organization'],
                                     format_func=lambda value: 'Tema' if value == 'Theme' else 'Organización')
        entity_name = col2.text_input('Nombre exacto de entidad (opcional)', max_chars=256)
        record_limit = col3.selectbox('Registros de muestra', [1, 2, 3, 4, 5], index=2)
        st.form_submit_button('Explorar conexiones')
    rows = graph_sample(target_date, entity_type, entity_name, record_limit)
    if not rows:
        st.info('No hay registros en el grafo para esta fecha y filtro.')
        return
    st.plotly_chart(graph_figure(rows), width='stretch', key='relationship_graph')
    sampled = len({row['record_id'] for row in rows})
    edges = sum(bool(row.get('relationship')) for row in rows)
    st.caption(f'Muestra de {sampled} registros y {edges} relaciones. '
               'El grafo conserva hasta las primeras diez entradas de temas y organizaciones por registro. '
               'La muestra no representa un ranking global.')
    with st.expander('Ver relaciones de la muestra'):
        st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)


st.title('🌍 Global News Intelligence')
st.caption('Observatorio de información global · GDELT · Ejecución local')
if st.button('Actualizar datos', key='refresh_data'):
    st.cache_data.clear()

# Cada fuente falla de forma independiente; un error Cassandra no oculta MongoDB o Neo4j.
df = pd.DataFrame()
cassandra_available = True
try:
    df = get_daily_metrics()
except Exception:
    cassandra_available = False
mongo_dates = []
try:
    mongo_dates = document_dates()
except Exception:
    pass
options = sorted(set(mongo_dates) | (set(df['fecha']) if not df.empty else set()), reverse=True)
if options:
    selected_date = st.selectbox('Fecha de análisis', options=options,
                                 format_func=lambda value: value.strftime('%d/%m/%Y'), key='analysis_date')
else:
    selected_date = st.date_input('Fecha de análisis', value=date.today())
target_date = selected_date.strftime('%Y%m%d')
st.caption('La fecha seleccionada filtra rankings, documentos y relaciones. '
           'Las tarjetas de último día muestran la fecha más reciente de Cassandra.')

indicators_tab, documents_tab, graph_tab = st.tabs(['Indicadores · Cassandra',
                                                   'Documentos · MongoDB', 'Relaciones · Neo4j'])
with indicators_tab:
    if not cassandra_available:
        st.warning('Cassandra no está disponible. Puedes consultar las otras vistas.')
    elif df.empty:
        st.info('No hay métricas diarias en Cassandra.')
    else:
        try:
            render_indicators(df, selected_date)
        except Exception:
            st.warning('No se pudieron completar los indicadores de Cassandra.')
with documents_tab:
    try:
        render_documents(target_date)
    except Exception:
        st.warning('No se pudieron consultar los documentos de MongoDB.')
with graph_tab:
    try:
        render_graph(target_date)
    except Exception:
        st.warning('No se pudo consultar Neo4j. Comprueba que el servicio y su configuración estén disponibles.')
