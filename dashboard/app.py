"""Dashboard local: indicadores Cassandra, documentos MongoDB y relaciones Neo4j."""

import html
import math
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from pymongo import MongoClient
from neo4j import GraphDatabase

from dashboard import queries
from dashboard.graph import graph_figure
from dashboard.icons import icon, mark, brand_mark, pipeline_diagram
from src.transformation.aggregate_snapshot import active_entity_metrics
from src.config import MONGO_URI, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from src.config import CASSANDRA_HOST, CASSANDRA_PORT, CASSANDRA_KEYSPACE


# ---------------------------------------------------------------------------
# Configuración de página y estilos
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Global News Intelligence",
    page_icon=":material/public:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Paleta: azul como color de marca; cada base de datos conserva siempre el mismo color.
BLUE, PURPLE, GREEN = "#4f9cf9", "#a78bfa", "#34d399"
AMBER, RED, SLATE = "#f59e0b", "#f87171", "#8b9bb4"
MUTED_BAR = "#27385a"
DB_COLOR = {"MongoDB": BLUE, "Cassandra": AMBER, "Neo4j": GREEN}
FONT = "'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, button, input, select, textarea { font-family: 'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif; }
    .stApp { background: #0b1220; }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1200px; padding-top: 1.4rem; padding-bottom: 5rem; }
    div[data-testid="stVerticalBlock"] { gap: 1rem; }
    /* Pestañas */
    div[data-baseweb="tab-list"] { gap: 28px; border-bottom: 1px solid #1e2b44; }
    button[data-baseweb="tab"] { background: transparent; padding: 12px 2px; color: #8b9bb4; font-weight: 500; font-size: 0.95rem; }
    button[data-baseweb="tab"]:hover { color: #e8eef8; background: transparent; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #e8eef8; font-weight: 600; }
    div[data-baseweb="tab-highlight"] { background-color: #4f9cf9; height: 2px; }
    div[data-baseweb="tab-panel"] { padding-top: 0.5rem; }
    /* Portada */
    .hero { border: 1px solid #1e2b44; border-radius: 18px; padding: 30px 34px;
            background: linear-gradient(120deg, #0f1c36 0%, #0d1730 60%, #0b1426 100%); }
    .hero-row { display: flex; align-items: center; gap: 22px; }
    .hero-title { font-size: 2rem; font-weight: 700; color: #f4f7fb; letter-spacing: -0.02em; line-height: 1.15; }
    .hero-sub { color: #a9b8cd; margin-top: 6px; font-size: 1rem; max-width: 640px; line-height: 1.5; }
    .status { margin-top: 22px; padding-top: 16px; border-top: 1px solid #1e2b44; display: flex;
              flex-wrap: wrap; gap: 6px 26px; color: #a9b8cd; font-size: 0.86rem; align-items: center; }
    .status .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }
    .status .ok { background: #34d399; } .status .down { background: #f87171; }
    .status .src { color: #6c7d99; margin-left: auto; }
    /* Secciones */
    .sec { margin: 3.2rem 0 1.2rem 0; }
    .sec-eyebrow { font-size: 0.85rem; font-weight: 600; margin-bottom: 2px; }
    .sec-title { font-size: 1.55rem; font-weight: 700; color: #f4f7fb; letter-spacing: -0.02em; line-height: 1.25; }
    .sec-sub { color: #8b9bb4; font-size: 0.95rem; margin-top: 6px; max-width: 760px; line-height: 1.55; }
    /* Texto */
    .lead { color: #c3cfe3; font-size: 1.02rem; line-height: 1.75; max-width: 820px; }
    .note { border-left: 2px solid #2a3f66; padding: 2px 0 2px 16px; color: #9fb0c9; font-size: 0.88rem;
            line-height: 1.65; max-width: 860px; }
    .chart-title { font-size: 1.05rem; font-weight: 600; color: #f1f5fb; line-height: 1.4; margin-bottom: 2px; }
    .chart-sub { color: #8b9bb4; font-size: 0.84rem; margin-bottom: 6px; }
    /* KPI: la única pieza en forma de ficha */
    .kpi { background: #111a2b; border: 1px solid #1e2b44; border-radius: 14px; padding: 20px 22px; height: 100%; }
    .kpi-head { display: flex; justify-content: space-between; align-items: center; }
    .kpi-tag { font-size: 0.78rem; color: #6c7d99; font-weight: 500; }
    .kpi-label { color: #a9b8cd; font-size: 0.9rem; margin-top: 14px; }
    .kpi-value { color: #f4f7fb; font-size: 2.1rem; font-weight: 700; line-height: 1.2; letter-spacing: -0.02em; margin-top: 2px; }
    .kpi-note { color: #7f92b0; font-size: 0.82rem; margin-top: 8px; line-height: 1.45; }
    /* Definiciones: lista limpia, sin cajas */
    .deflist { max-width: 980px; border-top: 1px solid #1e2b44; }
    .def-row { display: grid; grid-template-columns: 210px 1fr; gap: 28px; padding: 16px 0; border-bottom: 1px solid #1e2b44; }
    .def-key { color: #f1f5fb; font-weight: 600; font-size: 0.98rem; }
    .def-val { color: #a9b8cd; font-size: 0.93rem; line-height: 1.65; }
    /* Bases de datos: columnas sin caja, separadas por una línea de color */
    .plain-col { border-top: 2px solid var(--accent); padding-top: 18px; padding-right: 10px; }
    .plain-head { display: flex; align-items: center; gap: 12px; font-size: 1.15rem; font-weight: 700; color: #f4f7fb; }
    .plain-model { color: var(--accent); font-size: 0.86rem; font-weight: 600; margin: 8px 0 10px 0; }
    .plain-col p { color: #a9b8cd; font-size: 0.92rem; line-height: 1.65; margin: 0 0 10px 0; }
    .plain-col .adv { color: #c3cfe3; font-size: 0.88rem; border-top: 1px solid #1e2b44; padding-top: 10px; margin-top: 12px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers de presentación
# ---------------------------------------------------------------------------
def spacer(px_height=28):
    st.markdown(f'<div style="height:{px_height}px"></div>', unsafe_allow_html=True)


def kpi_card(icon_name, label, value, note="", accent=BLUE, tag=""):
    tag_html = f'<span class="kpi-tag">{tag}</span>' if tag else ""
    return (f'<div class="kpi"><div class="kpi-head">{icon(icon_name, 22, accent)}{tag_html}</div>'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>'
            f'<div class="kpi-note">{note}</div></div>')


def section(title, subtitle="", db="", **_):
    """Encabezado de sección. `db` indica de qué base sale la información (con su color)."""
    eyebrow = (f'<div class="sec-eyebrow" style="color:{DB_COLOR.get(db, BLUE)}">Datos de {db}</div>'
               if db else "")
    sub = f'<div class="sec-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div class="sec">{eyebrow}<div class="sec-title">{title}</div>{sub}</div>',
                unsafe_allow_html=True)


def lead(text):
    st.markdown(f'<div class="lead">{text}</div>', unsafe_allow_html=True)


def note(text):
    st.markdown(f'<div class="note">{text}</div>', unsafe_allow_html=True)


def chart_head(title, sub=""):
    """Título del gráfico escrito como conclusión, no como nombre de la variable."""
    sub_html = f'<div class="chart-sub">{html.escape(sub)}</div>' if sub else ""
    st.markdown(f'<div class="chart-title">{html.escape(title)}</div>{sub_html}', unsafe_allow_html=True)


def deflist(rows):
    """Definiciones en lista limpia: término a la izquierda, explicación a la derecha."""
    body = "".join(f'<div class="def-row"><div class="def-key">{k}</div><div class="def-val">{v}</div></div>'
                   for k, v in rows)
    st.markdown(f'<div class="deflist">{body}</div>', unsafe_allow_html=True)


def query_block(question, code, language, caption=""):
    with st.expander(f":material/code: Consulta detrás de este resultado: {question}"):
        st.code(code, language=language)
        if caption:
            st.caption(caption)


def plot(fig, key=None):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=key)


def short(text, n):
    text = str(text)
    return text if len(text) <= n else text[:n - 1] + "…"


def fmt_date(value):
    return value.strftime("%d/%m/%Y")


def base_layout(fig, height, **kwargs):
    fig.update_layout(template="plotly_dark", height=height,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=FONT, color="#c3cfe3", size=13), **kwargs)
    fig.update_xaxes(gridcolor="rgba(139,155,180,0.10)", zerolinecolor="rgba(139,155,180,0.25)")
    fig.update_yaxes(gridcolor="rgba(139,155,180,0.10)", zerolinecolor="rgba(139,155,180,0.25)")
    return fig


def tone_label(value):
    if pd.isna(value):
        return "Sin dato"
    if value <= -2:
        return "Tono marcadamente negativo"
    if value < -0.5:
        return "Tono ligeramente negativo"
    if value <= 0.5:
        return "Tono neutral"
    if value < 2:
        return "Tono ligeramente positivo"
    return "Tono marcadamente positivo"


def row_for(df, target):
    if df.empty:
        return None
    match = df[df["fecha"] == target]
    return None if match.empty else match.iloc[-1]


def safe(function, *args):
    """Ejecuta una consulta; si falla devuelve None para que el resto de la vista siga funcionando."""
    try:
        return function(*args)
    except Exception:
        return None


def pct(part, whole):
    return part / whole * 100 if whole else 0.0


# ---------------------------------------------------------------------------
# Conexiones y datos
# ---------------------------------------------------------------------------
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


@st.cache_resource
def get_mongo_client():
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)


@st.cache_resource
def get_neo4j_driver():
    auth = (NEO4J_USER, NEO4J_PASSWORD) if NEO4J_PASSWORD else None
    driver = GraphDatabase.driver(NEO4J_URI, auth=auth,
                                  connection_timeout=5)
    try:
        driver.verify_connectivity()
    except Exception:
        driver.close()
        raise
    return driver


@st.cache_data(ttl=60)
def get_daily_metrics():
    session = get_cassandra_session()
    rows = session.execute("""
        SELECT news_date, total_records, unique_themes, average_tone
        FROM daily_news_metrics
        WHERE metric_group = 'global'
    """)
    data = [{
        "fecha": row.news_date.date(),
        "registros": row.total_records,
        "temas_unicos": row.unique_themes,
        "tono_promedio": row.average_tone,
    } for row in rows]
    df = pd.DataFrame(data, columns=["fecha", "registros", "temas_unicos", "tono_promedio"])
    if not df.empty:
        df = df.sort_values("fecha").reset_index(drop=True)
        previous = df["registros"].shift(1)
        df["variacion_pct"] = (df["registros"] - previous) / previous.where(previous > 0) * 100
    return df


@st.cache_data(ttl=60)
def get_top_themes(target_date):
    session = get_cassandra_session()
    rows = active_entity_metrics(session, target_date, 'theme')
    df = pd.DataFrame([{"tema": r.theme, "registros": r.record_count} for r in rows],
                      columns=["tema", "registros"])
    if not df.empty:
        df = df.sort_values("registros", ascending=False).head(10).reset_index(drop=True)
    return df


@st.cache_data(ttl=60)
def get_top_organizations(target_date):
    session = get_cassandra_session()
    rows = active_entity_metrics(session, target_date, 'organization')
    df = pd.DataFrame([{"organizacion": r.organization, "registros": r.record_count} for r in rows],
                      columns=["organizacion", "registros"])
    if not df.empty:
        df = df.sort_values("registros", ascending=False).head(10).reset_index(drop=True)
    return df


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


# KPIs de red: consultas más pesadas, se cachean 5 minutos.
@st.cache_data(ttl=300, show_spinner=False)
def graph_overview(target_date):
    return queries.get_graph_overview(get_neo4j_driver(), target_date)


@st.cache_data(ttl=300, show_spinner=False)
def graph_degrees(target_date):
    return queries.get_degree_distribution(get_neo4j_driver(), target_date)


@st.cache_data(ttl=300, show_spinner=False)
def graph_cooccurrence(target_date):
    return queries.get_org_cooccurrence(get_neo4j_driver(), target_date)


@st.cache_data(ttl=300, show_spinner=False)
def graph_top_entities(target_date, entity_type):
    return queries.get_top_entities(get_neo4j_driver(), target_date, entity_type)


@st.cache_data(ttl=300, show_spinner=False)
def graph_profile(target_date, entity_type, entity_name):
    return queries.get_entity_profile(get_neo4j_driver(), target_date, entity_type, entity_name)


# ---------------------------------------------------------------------------
# Pestaña 1: Panorama
# ---------------------------------------------------------------------------
def render_overview(df, status, day_total, selected_date):
    total = f"{int(df['registros'].sum()):,}" if not df.empty else "N/D"
    n_dates = len(df) if not df.empty else "N/D"

    section("Qué hace este proyecto", "Del dato crudo de GDELT a indicadores, documentos y relaciones")
    lead("Procesamos los <b>registros GDELT GKG</b> (Global Knowledge Graph). Cada fila resume lo que la prensa "
         "mundial publicó e incluye <b>temas, organizaciones y tono informativo</b>. Un pipeline diario en "
         "<b>Apache Airflow</b> descarga, valida, transforma y reparte los datos en <b>tres bases especializadas</b>; "
         "este tablero consulta cada una para lo que hace mejor.")
    spacer(8)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    c1.markdown(kpi_card("layers", "Registros analizados", total, "Suma de todas las fechas cargadas", BLUE),
                unsafe_allow_html=True)
    c2.markdown(kpi_card("calendar", "Fechas cargadas", str(n_dates), "La carga es diaria, pero no siempre consecutiva",
                         PURPLE), unsafe_allow_html=True)
    c3.markdown(kpi_card("file-text", f"Registros del {fmt_date(selected_date)}", f"{day_total:,}" if day_total else "N/D",
                         "Fecha seleccionada, según Cassandra", GREEN), unsafe_allow_html=True)
    c4.markdown(kpi_card("database", "Bases conectadas", f"{sum(status.values())} de 3",
                         "MongoDB, Cassandra y Neo4j", AMBER), unsafe_allow_html=True)

    section("Cómo viajan los datos", "Un DAG de ocho tareas en Airflow. Cada ejecución se marca como completa solo "
            "después de reconciliar las tres bases y publicar los seis indicadores.")
    st.markdown(pipeline_diagram(), unsafe_allow_html=True)

    section("Una base para cada tipo de pregunta", "Persistencia políglota: cada motor guarda el mismo dato en la forma que mejor responde")
    dbs = [
        ("mongodb", "file-text", "MongoDB", "Modelo documental", BLUE,
         "Conserva el registro completo, con listas y campos semiestructurados. Alimenta el explorador de documentos, con filtros y paginación.",
         "Esquema flexible y búsqueda por campos anidados."),
        ("cassandra", "server", "Cassandra", "Modelo columnar", AMBER,
         "Materializa los KPIs por fecha, con una partición por día. Alimenta volumen, variación, diversidad, tono y rankings.",
         "Lecturas rápidas y escalado horizontal; escritura versionada con UUID."),
        ("neo4j", "share", "Neo4j", "Modelo de grafos", GREEN,
         "Conecta registros con temas y organizaciones (HAS_THEME, MENTIONS_ORG). Alimenta los KPIs de red, las co-ocurrencias y el grafo interactivo.",
         "Recorre relaciones sin uniones costosas."),
    ]
    for col, (asset, fallback, name, model, accent, text, adv) in zip(st.columns(3, gap="large"), dbs):
        col.markdown(f'<div class="plain-col" style="--accent:{accent}">'
                     f'<div class="plain-head">{mark(asset, fallback, 30, accent)}<span>{name}</span></div>'
                     f'<div class="plain-model">{model}</div><p>{text}</p>'
                     f'<p class="adv"><b>Ventaja:</b> {adv}</p></div>', unsafe_allow_html=True)

    section("Big Data en este proyecto", "Las cinco V aplicadas a nuestro caso")
    deflist([
        ("Volumen", "Cientos de miles de registros: decenas de miles por día y cientos de miles de relaciones en el grafo."),
        ("Velocidad", "Ingesta diaria automatizada con Airflow (06:00 UTC), con reintentos e idempotencia."),
        ("Variedad", "JSONL semiestructurado que se convierte en documentos, tablas columnares y un grafo."),
        ("Veracidad", "Validación, deduplicación y reconciliación de conteos entre las tres bases."),
        ("Valor", "Seis KPIs de negocio más indicadores de red sobre temas, tono y entidades."),
    ])

    section("Preguntas de negocio que responde", "Cada indicador existe para resolver una pregunta concreta")
    st.dataframe(pd.DataFrame([
        ("¿Cuánta información se produce y cómo cambia?", "KPI 1 Volumen y KPI 2 Variación", "Cassandra"),
        ("¿De qué se habla y qué tan amplia es la agenda?", "KPI 3 Top temas y KPI 4 Diversidad", "Cassandra"),
        ("¿Con qué sentimiento se cuenta el mundo?", "KPI 5 Tono promedio", "Cassandra"),
        ("¿Quiénes protagonizan las noticias?", "KPI 6 Top organizaciones", "Cassandra"),
        ("¿Es la agenda concentrada o dispersa?", "R1 Concentración top 10 y R2 Cola larga", "Neo4j"),
        ("¿Qué tan rica en conexiones es cada noticia?", "R3 Conectividad por registro", "Neo4j"),
        ("¿Qué actores aparecen juntos?", "R4 Co-ocurrencia de organizaciones", "Neo4j"),
        ("¿Con qué narrativa se asocia un actor, o quién protagoniza un tema?", "R5 Perfil de entidad", "Neo4j"),
        ("¿Cómo se ve un registro con todo su contexto?", "Explorador documental", "MongoDB"),
    ], columns=["Pregunta", "Indicador", "Base"]), width="stretch", hide_index=True)

    section("Diccionario de datos", "Campos principales del registro GKG normalizado")
    deflist([
        ("<code>_id</code>", "Identificador derivado de archivo y fila (los archivos diarios se asumen inmutables). Se usa en MongoDB y Neo4j."),
        ("<code>date</code>", "Fecha de la partición diaria del registro, en formato YYYYMMDD. Se usa en todas las bases."),
        ("<code>themes</code>", "Lista de códigos temáticos de GDELT presentes en el registro. Alimenta los KPI 3 y 4 y el grafo."),
        ("<code>organizations</code>", "Lista de organizaciones mencionadas en el registro. Alimenta el KPI 6 y el grafo."),
        ("<code>tone_raw</code>", "Texto numérico; su primer componente es el tono promedio (de negativo a positivo). Alimenta el KPI 5."),
        ("<code>num_articles</code>", "Número de artículos asociados al registro GKG. Se consulta en MongoDB."),
    ])

    spacer(20)
    with st.expander(":material/info: Limitaciones que conviene conocer"):
        st.markdown(
            "- Un registro GKG **puede agrupar varios artículos**: los conteos no son noticias únicas.\n"
            "- El grafo conserva hasta **diez entradas** de temas y organizaciones por registro; los KPIs de red "
            "describen ese grafo truncado, no el universo completo de GDELT.\n"
            "- La co-ocurrencia se calcula entre las **40 organizaciones más mencionadas** del día para mantener la consulta acotada.\n"
            "- El histórico contiene **fechas puntuales**, por lo que la variación se calcula contra la fecha anterior disponible.\n"
            "- Los rankings de Cassandra se ordenan en Python tras leer la versión activa."
        )


# ---------------------------------------------------------------------------
# Pestaña 2: Indicadores (Cassandra)
# ---------------------------------------------------------------------------
def render_ranking(data, label_col, accent, total_day, noun, caption):
    if data.empty:
        st.info("No hay datos para esta fecha.")
        return
    data = data.copy()
    top_name, top_n = data.iloc[0][label_col], int(data.iloc[0]["registros"])
    if total_day:
        data["cobertura_pct"] = data["registros"] / total_day * 100
        chart_head(f"«{short(top_name, 60)}» lidera: aparece en {pct(top_n, total_day):.1f}% de los registros del día",
                   f"Top 10 de {noun}, medido en registros GKG")
    else:
        chart_head(f"«{short(top_name, 60)}» lidera con {top_n:,} registros", f"Top 10 de {noun}")
    labels = data[label_col].astype(str).map(lambda v: short(v, 38))

    col_chart, col_table = st.columns([3, 2], gap="large")
    with col_chart:
        colors = [accent] + [MUTED_BAR] * (len(data) - 1)
        fig = go.Figure(go.Bar(
            x=data["registros"], y=labels, orientation="h",
            text=data["registros"], texttemplate="%{text:,}", textposition="outside", cliponaxis=False,
            customdata=data[label_col],
            hovertemplate="%{customdata}<br>%{x:,} registros<extra></extra>",
            marker_color=colors,
        ))
        base_layout(fig, 430, margin=dict(l=10, r=70, t=10, b=10), xaxis_title="Registros GKG",
                    yaxis=dict(autorange="reversed", automargin=True))
        plot(fig)
    with col_table:
        table = data.rename(columns={label_col: "Nombre", "registros": "Registros"})
        table.insert(0, "#", range(1, len(table) + 1))
        config = {"Registros": st.column_config.NumberColumn(format="%d")}
        if "cobertura_pct" in table:
            top = float(table["cobertura_pct"].max())
            config["cobertura_pct"] = st.column_config.ProgressColumn(
                "Cobertura", format="%.2f%%", min_value=0.0, max_value=max(top, 1.0))
        st.dataframe(table, width="stretch", hide_index=True, height=430, column_config=config)
    st.caption(caption)


def render_indicators(df, selected_date):
    row = row_for(df, selected_date)
    if row is None:
        row = df.iloc[-1]
        st.warning(f"No hay métricas de Cassandra para {fmt_date(selected_date)}. "
                   f"Se muestra la fecha más reciente disponible: {fmt_date(row['fecha'])}.")
    day = row["fecha"]
    previous = df[df["fecha"] < day]
    prev_row = previous.iloc[-1] if not previous.empty else None

    records = int(row["registros"])
    themes = int(row["temas_unicos"])
    tone = row["tono_promedio"]
    variation = row["variacion_pct"]
    total_all = int(df["registros"].sum())

    section("Resumen del día", f"Métricas del {fmt_date(day)} calculadas por el pipeline y servidas desde Cassandra",
            "Cassandra")
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    c1.markdown(kpi_card("layers", "Registros del día", f"{records:,}",
                         f"Acumulado: {total_all:,} en {len(df)} fechas", BLUE, "KPI 1"), unsafe_allow_html=True)
    if pd.notna(variation) and prev_row is not None:
        arrow = "▲" if variation >= 0 else "▼"
        c2.markdown(kpi_card("trending-up" if variation >= 0 else "trending-down", "Variación vs. fecha anterior",
                             f"{arrow} {variation:+.2f}%",
                             f"Base: {fmt_date(prev_row['fecha'])} ({int(prev_row['registros']):,} registros)",
                             GREEN if variation >= 0 else RED, "KPI 2"), unsafe_allow_html=True)
    else:
        c2.markdown(kpi_card("trending-up", "Variación vs. fecha anterior", "N/D",
                             "Requiere una fecha anterior con registros", SLATE, "KPI 2"), unsafe_allow_html=True)
    density = themes / records * 1000 if records else 0
    c3.markdown(kpi_card("compass", "Diversidad temática", f"{themes:,}",
                         f"≈ {density:,.0f} temas distintos por cada 1.000 registros", PURPLE, "KPI 4"),
                unsafe_allow_html=True)
    c4.markdown(kpi_card("gauge", "Tono promedio", f"{tone:+.2f}" if pd.notna(tone) else "N/D",
                         tone_label(tone), AMBER, "KPI 5"), unsafe_allow_html=True)
    spacer(6)
    note("La variación se calcula contra la <b>fecha anterior disponible</b>, no necesariamente el día previo. "
         "El tono de GDELT va aproximadamente de −10 (muy negativo) a +10 (muy positivo).")

    # ---- Evolución ----
    section("Cómo evoluciona la cobertura", "La barra resaltada es la fecha seleccionada", "Cassandra")
    labels = df["fecha"].map(fmt_date)
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        peak = df.loc[df["registros"].idxmax()]
        if len(df) > 1:
            chart_head(f"El mayor volumen fue el {fmt_date(peak['fecha'])}: {int(peak['registros']):,} registros",
                       "Registros GKG por fecha de carga")
        else:
            chart_head(f"Solo hay una fecha cargada: {records:,} registros", "Registros GKG por fecha de carga")
        colors = [BLUE if d == day else MUTED_BAR for d in df["fecha"]]
        fig = go.Figure(go.Bar(x=labels, y=df["registros"], marker_color=colors,
                               text=df["registros"], texttemplate="%{text:,}", textposition="outside",
                               cliponaxis=False, hovertemplate="%{x}<br>%{y:,} registros<extra></extra>"))
        base_layout(fig, 340, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="Registros",
                    xaxis=dict(type="category"))
        fig.update_yaxes(rangemode="tozero", tickformat=",d")
        plot(fig)
    with col_b:
        var = df["variacion_pct"]
        if var.notna().any():
            big = df.loc[var.abs().idxmax()]
            chart_head(f"La mayor variación entre cargas fue {big['variacion_pct']:+.1f}% ({fmt_date(big['fecha'])})",
                       "Cambio porcentual frente a la fecha anterior; verde sube, rojo baja")
            colors = [SLATE if pd.isna(v) else (GREEN if v >= 0 else RED) for v in var]
            fig = go.Figure(go.Bar(x=labels, y=var, marker_color=colors,
                                   text=var.map(lambda v: "" if pd.isna(v) else f"{v:+.1f}%"),
                                   textposition="outside", cliponaxis=False,
                                   hovertemplate="%{x}<br>%{y:+.2f}%<extra></extra>"))
            base_layout(fig, 340, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="Variación (%)",
                        xaxis=dict(type="category"))
            fig.add_hline(y=0, line_dash="dash", line_color=SLATE)
            plot(fig)
        else:
            chart_head("La variación necesita al menos dos fechas cargadas")
            st.info("Aún no hay una fecha anterior contra la cual comparar.")

    # ---- Rankings ----
    section("Quién y de qué se habla", f"Los diez temas y organizaciones más presentes el {fmt_date(day)}", "Cassandra")
    tab_t, tab_o = st.tabs([":material/sell: Temas más mencionados (KPI 3)",
                            ":material/corporate_fare: Organizaciones más mencionadas (KPI 6)"])
    with tab_t:
        spacer(8)
        render_ranking(get_top_themes(day), "tema", PURPLE, records, "temas",
                       "Cobertura = % de registros del día que contienen el tema. Un registro puede tener varios "
                       "temas, por eso las coberturas no suman 100 %.")
    with tab_o:
        spacer(8)
        render_ranking(get_top_organizations(day), "organizacion", GREEN, records, "organizaciones",
                       "Entidades extraídas del campo de organizaciones de GDELT, contadas una vez por registro.")

    # ---- Diversidad y tono ----
    section("Amplitud de la agenda y tono informativo", "¿Cuántos temas distintos aparecen y con qué sentimiento?",
            "Cassandra")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        chart_head(f"{themes:,} temas distintos el {fmt_date(day)}", "Diversidad temática por fecha (KPI 4)")
        fig = go.Figure(go.Scatter(x=labels, y=df["temas_unicos"], mode="lines+markers",
                                   line=dict(color=PURPLE, width=3), marker=dict(size=9, color=PURPLE),
                                   hovertemplate="%{x}<br>%{y:,} temas<extra></extra>"))
        fig.add_trace(go.Scatter(x=[fmt_date(day)], y=[themes], mode="markers", showlegend=False,
                                 marker=dict(size=17, color="rgba(0,0,0,0)", line=dict(color="#f4f7fb", width=2)),
                                 hoverinfo="skip"))
        base_layout(fig, 340, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="Temas distintos",
                    xaxis=dict(type="category"))
        fig.update_yaxes(rangemode="tozero", tickformat=",d")
        plot(fig)
    with col2:
        tones = df["tono_promedio"].dropna()
        chart_head(f"{tone_label(tone)} ({tone:+.2f})" if pd.notna(tone) else "Tono sin dato",
                   "Tono promedio por fecha (KPI 5); la franja gris es la zona neutral")
        if not tones.empty:
            lo, hi = min(-4.0, float(tones.min()) - 0.5), max(4.0, float(tones.max()) + 0.5)
            fig = go.Figure(go.Scatter(x=labels, y=df["tono_promedio"], mode="lines+markers",
                                       line=dict(color=AMBER, width=3), marker=dict(size=9, color=AMBER),
                                       hovertemplate="%{x}<br>Tono %{y:+.3f}<extra></extra>"))
            fig.add_hrect(y0=-2, y1=2, fillcolor=SLATE, opacity=0.10, line_width=0)
            fig.add_hline(y=0, line_dash="dash", line_color=SLATE)
            if pd.notna(tone):
                fig.add_trace(go.Scatter(x=[fmt_date(day)], y=[float(tone)], mode="markers", showlegend=False,
                                         marker=dict(size=17, color="rgba(0,0,0,0)",
                                                     line=dict(color="#f4f7fb", width=2)), hoverinfo="skip"))
            base_layout(fig, 340, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="Tono",
                        xaxis=dict(type="category"))
            fig.update_yaxes(range=[lo, hi])
            plot(fig)

    # ---- Guía y consultas ----
    section("Cómo leer los indicadores", "Definición de cada KPI y consulta que lo alimenta")
    deflist([
        ("KPI 1 Volumen", "Registros GKG por día y suma del período. Mide la intensidad de la cobertura informativa."),
        ("KPI 2 Variación", "100 × (R actual − R anterior) / R anterior; N/D si no hay base positiva. Detecta picos o caídas de actividad."),
        ("KPI 3 Top 10 temas", "Registros que contienen cada tema (una contribución por registro y tema). Revela de qué se habla más."),
        ("KPI 4 Diversidad", "Códigos temáticos distintos por fecha. Más temas significa una agenda más amplia."),
        ("KPI 5 Tono", "Promedio del primer componente numérico de tone_raw. Indica si el tono es negativo, neutral o positivo."),
        ("KPI 6 Top 10 organizaciones", "Registros que contienen cada organización (deduplicado por registro). Muestra qué actores dominan las noticias."),
    ])
    spacer(12)
    query_block("¿Cuánta información se produce y cómo cambia?",
                "SELECT news_date, total_records, unique_themes, average_tone\n"
                "FROM daily_news_metrics\n"
                "WHERE metric_group = 'global';",
                "sql",
                "Cassandra sirve estas lecturas por partición. La variación y los rankings se calculan en Python sobre el resultado.")
    with st.expander(":material/table_chart: Ver datos diarios"):
        st.dataframe(df, width="stretch", hide_index=True, column_config={
            "fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
            "registros": st.column_config.NumberColumn("Registros GKG", format="%d"),
            "temas_unicos": st.column_config.NumberColumn("Temas distintos", format="%d"),
            "tono_promedio": st.column_config.NumberColumn("Tono", format="%+.3f"),
            "variacion_pct": st.column_config.NumberColumn("Variación (%)", format="%.2f%%"),
        })

    spacer(10)
    st.caption("Fuente: GDELT GKG. Procesamiento: Airflow hacia MongoDB, Cassandra y Neo4j. "
               "Los registros GKG no equivalen a artículos únicos.")


# ---------------------------------------------------------------------------
# Pestaña 3: Documentos (MongoDB)
# ---------------------------------------------------------------------------
def render_documents(target_date, day_total):
    section("Explorador documental",
            f"Registros normalizados del {target_date[6:8]}/{target_date[4:6]}/{target_date[:4]}", "MongoDB")
    note("MongoDB guarda cada registro tal como llega, con listas de temas y organizaciones de longitud variable. "
         "Filtra por <b>tema exacto</b> (con índice sobre la lista) o por <b>organización</b> "
         "(búsqueda literal, sin distinguir mayúsculas).")
    spacer(4)
    with st.form('document_filters'):
        col1, col2 = st.columns(2)
        theme = col1.text_input('Tema: código exacto', max_chars=128)
        organization = col2.text_input('Organización: contiene', max_chars=128)
        col1, col2 = st.columns(2)
        page = col1.number_input('Página', min_value=1, value=1, step=1)
        page_size = col2.selectbox('Registros por página', [20, 50, 100])
        st.form_submit_button('Consultar documentos', icon=":material/search:")
    result = documents(target_date, theme, organization, int(page), page_size)
    total = result['total']
    pages = max(1, math.ceil(total / page_size))

    spacer(4)
    c1, c2, c3 = st.columns(3, gap="medium")
    c1.markdown(kpi_card("search", "Registros encontrados", f"{total:,}", "Según los filtros aplicados", BLUE),
                unsafe_allow_html=True)
    share = f"{total / day_total * 100:.2f}%" if day_total else "N/D"
    c2.markdown(kpi_card("target", "Proporción del día", share, "Respecto al total de Cassandra", PURPLE),
                unsafe_allow_html=True)
    c3.markdown(kpi_card("file-text", "Página", f"{int(page)} de {pages:,}", f"{page_size} registros por página", GREEN),
                unsafe_allow_html=True)

    items = result['documents']
    if not items:
        st.info('No hay registros en esta página para los filtros seleccionados.')
        return

    spacer(10)
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

    section("Qué tan distintos son los registros", "Muestra: la página que estás viendo", "MongoDB")
    n_themes = [len(i.get('themes', [])) for i in items]
    n_orgs = [len(i.get('organizations', [])) for i in items]
    chart_head(f"Un registro típico trae {sum(n_themes) / len(items):.1f} temas y {sum(n_orgs) / len(items):.1f} organizaciones",
               "Su tamaño varía mucho: es el dato semiestructurado que encaja en un modelo documental")
    sizes = pd.DataFrame({"Temas": n_themes, "Organizaciones": n_orgs})
    fig = px.histogram(sizes, barmode="overlay", opacity=0.75, nbins=20, color_discrete_sequence=[PURPLE, GREEN])
    base_layout(fig, 300, margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="Elementos por registro", yaxis_title="Registros", legend_title="")
    plot(fig)

    section("Documento completo", "Elige un registro para ver todos sus campos")
    selected = st.selectbox('Registro', [item['_id'] for item in items],
                            format_func=lambda value: value[:20], key='document_id')
    st.json(next(item for item in items if item['_id'] == selected), expanded=False)
    spacer(8)
    query_block("¿Cómo se ve un registro con todo su contexto?",
                'db.registros.find({\n'
                '  "date": "<YYYYMMDD>",\n'
                '  "themes": "<código exacto>",\n'
                '  "organizations": { "$regex": "<texto>", "$options": "i" }\n'
                '}).skip((página - 1) * tamaño).limit(tamaño)',
                "javascript",
                "Patrón equivalente a la búsqueda del explorador; el nombre real de la colección puede variar.")
    st.caption('Un registro GKG puede agrupar varios artículos; el conteo no representa noticias únicas.')


# ---------------------------------------------------------------------------
# Pestaña 4: Relaciones (Neo4j)
# ---------------------------------------------------------------------------
ENTITY_LABELS = {'Theme': 'Tema', 'Organization': 'Organización'}

COOCCURRENCE_CYPHER = (
    "MATCH (r:GKGRecord {date: $date})-[:MENTIONS_ORG]->(o:Organization)\n"
    "WITH o, count(r) AS mentions ORDER BY mentions DESC LIMIT $top_n\n"
    "WITH collect(o) AS tops\n"
    "MATCH (r:GKGRecord {date: $date})-[:MENTIONS_ORG]->(x:Organization)\n"
    "WHERE x IN tops\n"
    "WITH r, collect(x) AS members WHERE size(members) > 1\n"
    "UNWIND members AS a UNWIND members AS b\n"
    "WITH a, b WHERE a.name < b.name\n"
    "RETURN a.name, b.name, count(*) AS records ORDER BY records DESC LIMIT 10")


def render_network_kpis(target_date, counts):
    """KPIs que solo un grafo responde bien: concentración, conectividad, co-ocurrencia y perfiles."""
    overview = safe(graph_overview, target_date)
    degrees = safe(graph_degrees, target_date)

    section("Qué tan concentrada está la agenda", "Cuántos actores dominan, cuántos aparecen una sola vez y cuán conectado está cada registro",
            "Neo4j")

    if overview:
        th, org = overview['Theme'], overview['Organization']
        entities = th['entities'] + org['entities']
        top10_t, top10_o = pct(th['top10'], th['mentions']), pct(org['top10'], org['mentions'])
        tail_t, tail_o = pct(th['singletons'], th['entities']), pct(org['singletons'], org['entities'])
        avg_degree = (counts['themes'] + counts['organizations']) / counts['records'] if counts['records'] else 0

        k1, k2, k3, k4 = st.columns(4, gap="medium")
        k1.markdown(kpi_card("users", "Entidades únicas", f"{entities:,}",
                             f"{th['entities']:,} temas y {org['entities']:,} organizaciones", BLUE, "R0"),
                    unsafe_allow_html=True)
        k2.markdown(kpi_card("target", "Concentración top 10", f"{top10_o:.1f}%",
                             f"Organizaciones. En temas: {top10_t:.1f}% de las menciones", PURPLE, "R1"),
                    unsafe_allow_html=True)
        k3.markdown(kpi_card("filter", "Cola larga", f"{tail_o:.1f}%",
                             f"Organizaciones con una sola mención. En temas: {tail_t:.1f}%", AMBER, "R2"),
                    unsafe_allow_html=True)
        k4.markdown(kpi_card("share", "Conectividad por registro", f"{avg_degree:.1f}",
                             "Relaciones promedio (temas y organizaciones)", GREEN, "R3"), unsafe_allow_html=True)
        spacer(8)
        deflist([
            ("Concentración top 10", "Qué parte de todas las menciones se la llevan las 10 entidades más citadas. Un valor alto indica una agenda dominada por pocos actores."),
            ("Cola larga", "Porcentaje de entidades mencionadas una sola vez. Un valor alto indica una agenda fragmentada."),
            ("Conectividad", "Cuántos temas y organizaciones enlaza un registro. Más enlaces significan más contexto por noticia."),
        ])
        spacer(14)

        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            chart_head(f"Diez organizaciones acumulan {top10_o:.0f}% de las menciones",
                       f"En temas, el top 10 reúne {top10_t:.0f}%; a la vez, muchas entidades aparecen una sola vez")
            fig = go.Figure()
            fig.add_bar(name="Top 10 (% de menciones)", x=["Temas", "Organizaciones"], y=[top10_t, top10_o],
                        marker_color=BLUE, text=[f"{top10_t:.1f}%", f"{top10_o:.1f}%"], textposition="outside")
            fig.add_bar(name="Una sola mención (% de entidades)", x=["Temas", "Organizaciones"], y=[tail_t, tail_o],
                        marker_color=AMBER, text=[f"{tail_t:.1f}%", f"{tail_o:.1f}%"], textposition="outside")
            base_layout(fig, 340, margin=dict(l=10, r=10, t=20, b=10), barmode="group", yaxis_title="%",
                        legend=dict(orientation="h", y=-0.18))
            fig.update_yaxes(rangemode="tozero", range=[0, 112])
            plot(fig)
        with col_b:
            if degrees:
                dist = pd.DataFrame(degrees)
                mean = float((dist["degree"] * dist["records"]).sum() / dist["records"].sum())
                chart_head(f"Cada registro enlaza en promedio {mean:.1f} temas y organizaciones",
                           f"Máximo observado: {int(dist['degree'].max())} relaciones; "
                           f"registros sin conexiones: {int(dist.loc[dist['degree'] == 0, 'records'].sum()):,}")
                fig = go.Figure(go.Bar(x=dist["degree"], y=dist["records"], marker_color=GREEN,
                                       hovertemplate="%{x} relaciones<br>%{y:,} registros<extra></extra>"))
                fig.add_vline(x=mean, line_dash="dash", line_color="#f4f7fb",
                              annotation_text=f"media {mean:.1f}", annotation_position="top")
                base_layout(fig, 340, margin=dict(l=10, r=10, t=20, b=10),
                            xaxis_title="Relaciones del registro", yaxis_title="Registros")
                plot(fig)
            else:
                chart_head("Distribución de conectividad")
                st.info("No se pudo calcular la distribución de conectividad.")
    else:
        st.info("No se pudieron calcular los KPIs de red para esta fecha.")

    # ---- R4: co-ocurrencia ----
    section("Actores que aparecen juntos", "Pares de organizaciones que comparten registros, entre las 40 más mencionadas", "Neo4j")
    pairs = safe(graph_cooccurrence, target_date)
    if pairs:
        data = pd.DataFrame(pairs)
        data["par"] = data["source"].map(lambda v: short(v, 26)) + "  y  " + data["target"].map(lambda v: short(v, 26))
        first = data.iloc[0]
        chart_head(f"«{short(first['source'], 30)}» y «{short(first['target'], 30)}» son el par que más coincide: "
                   f"{int(first['records']):,} registros",
                   "Registros en común por par de organizaciones")
        col_c, col_t = st.columns([3, 2], gap="large")
        with col_c:
            colors = [GREEN] + [MUTED_BAR] * (len(data) - 1)
            fig = go.Figure(go.Bar(
                x=data["records"], y=data["par"], orientation="h", text=data["records"],
                texttemplate="%{text:,}", textposition="outside", cliponaxis=False, marker_color=colors,
                hovertemplate="%{y}<br>%{x:,} registros en común<extra></extra>"))
            base_layout(fig, 420, margin=dict(l=10, r=60, t=10, b=10), xaxis_title="Registros en común",
                        yaxis=dict(autorange="reversed", automargin=True))
            plot(fig)
        with col_t:
            table = data[["source", "target", "records"]].rename(
                columns={"source": "Organización A", "target": "Organización B", "records": "Registros"})
            st.dataframe(table, width="stretch", hide_index=True, height=420,
                         column_config={"Registros": st.column_config.NumberColumn(format="%d")})
        st.caption("Dos organizaciones co-ocurren cuando un mismo registro GKG las menciona a ambas. "
                   "Indica contexto compartido, no una relación de causa o alianza formal.")
        query_block("¿Qué actores aparecen juntos?", COOCCURRENCE_CYPHER, "cypher",
                    "Este tipo de consulta es difícil de expresar con uniones en una base relacional.")
    elif pairs is None:
        st.info("No se pudo calcular la co-ocurrencia de organizaciones.")
    else:
        st.info("No hay co-ocurrencias entre las organizaciones más mencionadas para esta fecha.")

    # ---- R5: perfil de entidad ----
    section("Perfil de una entidad", "Con qué narrativa se asocia un actor, o quién protagoniza un tema", "Neo4j")
    c_type, c_name = st.columns([1, 3], gap="medium")
    entity_type = c_type.radio("Analizar", ["Organization", "Theme"], horizontal=False,
                               format_func=lambda v: ENTITY_LABELS[v], key="profile_type")
    top_entities = safe(graph_top_entities, target_date, entity_type) or []
    if not top_entities:
        st.info("No hay entidades disponibles para construir el perfil.")
        return
    names = [item['name'] for item in top_entities]
    chosen = c_name.selectbox(f"{ENTITY_LABELS[entity_type]} (las 25 más mencionadas)", names,
                              format_func=lambda v: v[:90], key=f"profile_name_{entity_type}")
    profile = safe(graph_profile, target_date, entity_type, chosen)
    if not profile or not profile['related']:
        st.info("No hay relaciones para esta entidad.")
        return
    related = pd.DataFrame(profile['related'])
    related["afinidad"] = related["records"] / profile['total'] * 100
    other = 'Theme' if entity_type == 'Organization' else 'Organization'

    spacer(4)
    m1, m2 = st.columns(2, gap="medium")
    m1.markdown(kpi_card("file-text", "Registros que la mencionan", f"{profile['total']:,}",
                         f"{pct(profile['total'], counts['records']):.2f}% de los registros del día", BLUE, "R5"),
                unsafe_allow_html=True)
    m2.markdown(kpi_card("link", f"{ENTITY_LABELS[other]} más asociados", f"{len(related)}",
                         "Ordenados por registros en común", PURPLE, "R5"), unsafe_allow_html=True)
    spacer(8)
    best = related.loc[related["afinidad"].idxmax()]
    chart_head(f"Con «{short(chosen, 40)}» suele aparecer «{short(best['name'], 40)}» ({best['afinidad']:.0f}% de sus registros)",
               "Afinidad: porcentaje de los registros de la entidad que también incluyen cada elemento")
    accent = PURPLE if other == 'Theme' else GREEN
    colors = [accent if n == best['name'] else MUTED_BAR for n in related["name"]]
    fig = go.Figure(go.Bar(
        x=related["afinidad"], y=related["name"].astype(str).map(lambda v: short(v, 40)), orientation="h",
        customdata=related[["name", "records"]],
        text=related["afinidad"].map(lambda v: f"{v:.1f}%"), textposition="outside", cliponaxis=False,
        hovertemplate="%{customdata[0]}<br>%{customdata[1]:,} registros en común<extra></extra>",
        marker_color=colors))
    base_layout(fig, 400, margin=dict(l=10, r=60, t=10, b=10), xaxis_title="% de afinidad",
                yaxis=dict(autorange="reversed", automargin=True))
    plot(fig)
    st.caption("Afinidad = registros en común / registros que mencionan la entidad seleccionada. "
               "Un valor alto describe el contexto con el que suele aparecer.")


def render_graph(target_date, counts):
    section("Relaciones entre registros, temas y organizaciones",
            f"Datos del {target_date[6:8]}/{target_date[4:6]}/{target_date[:4]}", "Neo4j")
    note("En el grafo cada registro es un nodo conectado con los <b>temas</b> (HAS_THEME) y las "
         "<b>organizaciones</b> (MENTIONS_ORG) que menciona. Las consultas de red responden preguntas que en "
         "otras bases requerirían uniones costosas.")
    spacer(6)

    records = counts['records']
    per_record_t = counts['themes'] / records if records else 0
    per_record_o = counts['organizations'] / records if records else 0
    c1, c2, c3 = st.columns(3, gap="medium")
    c1.markdown(kpi_card("database", "Registros en Neo4j", f"{records:,}", "Nodos GKGRecord del día", BLUE),
                unsafe_allow_html=True)
    c2.markdown(kpi_card("hash", "Relaciones con temas", f"{counts['themes']:,}",
                         f"≈ {per_record_t:.1f} temas por registro", PURPLE), unsafe_allow_html=True)
    c3.markdown(kpi_card("briefcase", "Relaciones con organizaciones", f"{counts['organizations']:,}",
                         f"≈ {per_record_o:.1f} organizaciones por registro", GREEN), unsafe_allow_html=True)

    with st.spinner("Calculando KPIs de red..."):
        render_network_kpis(target_date, counts)

    section("Explora el grafo", "Muestra interactiva de registros con sus temas y organizaciones", "Neo4j")
    with st.form('graph_filters'):
        col1, col2, col3 = st.columns([1, 2, 1])
        entity_type = col1.selectbox('Tipo de entidad', ['Theme', 'Organization'],
                                     format_func=lambda value: ENTITY_LABELS[value])
        entity_name = col2.text_input('Nombre exacto de entidad (opcional)', max_chars=256)
        record_limit = col3.selectbox('Registros de muestra', [1, 2, 3, 4, 5], index=2)
        st.form_submit_button('Explorar conexiones', icon=":material/hub:")
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
    with st.expander(':material/table_rows: Ver relaciones de la muestra'):
        st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)


# ---------------------------------------------------------------------------
# Aplicación principal
# ---------------------------------------------------------------------------
# La portada se rellena al final, cuando ya se conoce el estado de cada base.
hero_slot = st.empty()

# Cada fuente falla de forma independiente; un error de una base no oculta las otras.
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

header_col, button_col = st.columns([6, 1], vertical_alignment="bottom")
with button_col:
    if st.button('Actualizar datos', key='refresh_data', icon=":material/refresh:"):
        st.cache_data.clear()

options = sorted(set(mongo_dates) | (set(df['fecha']) if not df.empty else set()), reverse=True)
with header_col:
    if options:
        selected_date = st.selectbox(':material/calendar_month: Fecha de análisis', options=options,
                                     format_func=fmt_date, key='analysis_date',
                                     help='Filtra indicadores, rankings, documentos y relaciones.')
    else:
        selected_date = st.date_input(':material/calendar_month: Fecha de análisis', value=date.today())
target_date = selected_date.strftime('%Y%m%d')

neo_counts = None
try:
    neo_counts = graph_counts(target_date)
except Exception:
    pass

status = {"Cassandra": cassandra_available and not df.empty,
          "MongoDB": bool(mongo_dates),
          "Neo4j": neo_counts is not None}

status_html = "".join(
    f'<span><i class="dot {"ok" if status[name] else "down"}"></i>{name}</span>'
    for name in ("MongoDB", "Cassandra", "Neo4j"))
hero_slot.markdown(
    '<div class="hero"><div class="hero-row">' + brand_mark(76) +
    '<div><div class="hero-title">Global News Intelligence</div>'
    '<div class="hero-sub">Observatorio de la prensa mundial construido sobre GDELT GKG, con tres bases de datos '
    'especializadas.</div></div></div>'
    f'<div class="status">{status_html}'
    '<span class="src">Fuente GDELT GKG, orquestación con Apache Airflow, ejecución local</span></div></div>',
    unsafe_allow_html=True)

sel_row = row_for(df, selected_date)
day_total = int(sel_row["registros"]) if sel_row is not None else None

spacer(6)
overview_tab, indicators_tab, documents_tab, graph_tab = st.tabs([
    ':material/explore: Panorama', ':material/monitoring: Indicadores',
    ':material/description: Documentos', ':material/hub: Relaciones'])

with overview_tab:
    render_overview(df, status, day_total, selected_date)
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
        render_documents(target_date, day_total)
    except Exception:
        st.warning('No se pudieron consultar los documentos de MongoDB.')
with graph_tab:
    if neo_counts is None:
        st.warning('No se pudo consultar Neo4j. Comprueba que el servicio y su configuración estén disponibles.')
    else:
        try:
            render_graph(target_date, neo_counts)
        except Exception:
            st.warning('No se pudo consultar Neo4j. Comprueba que el servicio y su configuración estén disponibles.')
