#Se conecta a Cassandra mediante el puerto 9043, que configuramos anteriormente en Docker.
#Consulta la tabla daily_news_metrics para recuperar los volúmenes diarios.
#Muestra dos métricas: registros totales del período y registros del último día.
#Genera un gráfico interactivo con Plotly.
#Utiliza caché para evitar consultar Cassandra continuamente.



import streamlit as st
import pandas as pd
import plotly.express as px

from cassandra.cluster import Cluster


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
    cluster = Cluster(["127.0.0.1"], port=9043)
    return cluster.connect("global_news_analytics")


# Datos diarios
@st.cache_data(ttl=300)
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
        df["variacion_pct"] = df["registros"].pct_change() * 100

    return df


# Consultar los 10 temas mas frecuentes de una fecha
@st.cache_data(ttl=300)
def get_top_themes(target_date):
    session = get_cassandra_session()

    rows = session.execute(
        """
        SELECT theme, record_count
        FROM daily_theme_metrics
        WHERE news_date = %s
        """,
        (target_date,)
    )

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
@st.cache_data(ttl=300)
def get_top_organizations(target_date):
    session = get_cassandra_session()

    rows = session.execute(
        """
        SELECT organization, record_count
        FROM daily_organization_metrics
        WHERE news_date = %s
        """,
        (target_date,)
    )

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

# Encabezado
st.title("🌍 Global News Intelligence")
st.caption(
    "Observatorio de informacion global | "
    "Datos reales de GDELT"
)

st.divider()


try:
    df = get_daily_metrics()

    if df.empty:
        st.warning("No se encontraron datos en Cassandra.")
        st.stop()

    # Metricas principales
    total = int(df["registros"].sum())
    latest = int(df.iloc[-1]["registros"])
    latest_date = df.iloc[-1]["fecha"]
    st.markdown("### Filtros de análisis")

    selected_date = st.selectbox(
        "Selecciona una fecha para los rankings",
        options=sorted(df["fecha"].tolist(), reverse=True),
        format_func=lambda date: date.strftime("%d/%m/%Y")
    )
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
            f"Fecha analizada: {latest_date} | "
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
        latest_tone = float(df.iloc[-1]["tono_promedio"])

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

            st.plotly_chart(
                fig_diversity,
                width="stretch",
                config={"displayModeBar": False}
            )

        with col2:
            st.metric(
                "Tono promedio del ultimo dia",
                f"{latest_tone:+.2f}"
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

except Exception as error:
    st.error("Error al consultar los datos.")
    st.exception(error)
