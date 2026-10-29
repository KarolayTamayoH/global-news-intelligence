
-- Base de datos analitica de Global News Intelligence
-- Cassandra: metricas y series temporales

CREATE KEYSPACE IF NOT EXISTS global_news_analytics
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

-- KPI 1: Volumen diario
-- KPI 4: Diversidad tematica
-- KPI 5: Tono promedio
CREATE TABLE IF NOT EXISTS global_news_analytics.daily_news_metrics (
    metric_group TEXT,
    news_date DATE,
    total_records BIGINT,
    unique_themes INT,
    average_tone DOUBLE,
    PRIMARY KEY (metric_group, news_date)
) WITH CLUSTERING ORDER BY (news_date DESC);

-- KPI 3: Frecuencia de temas por dia
CREATE TABLE IF NOT EXISTS global_news_analytics.daily_theme_metrics (
    news_date DATE,
    theme TEXT,
    record_count BIGINT,
    PRIMARY KEY (news_date, theme)
);

-- KPI 6: Organizaciones mencionadas por dia
CREATE TABLE IF NOT EXISTS global_news_analytics.daily_organization_metrics (
    news_date DATE,
    organization TEXT,
    record_count BIGINT,
    PRIMARY KEY (news_date, organization)
);
