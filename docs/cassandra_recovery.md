# Cassandra: publicación de agregados y recuperación

## Comportamiento

Cada intento calcula en una sola lectura MongoDB el volumen, diversidad, tono y
frecuencias de temas y organizaciones. Escribe las frecuencias con un UUID nuevo
en `daily_theme_metrics_versions` y `daily_organization_metrics_versions`, con
partición `(news_date, generation)`. Las escrituras tienen concurrencia acotada
a 32 y consistencia `LOCAL_QUORUM`.

Antes de publicar, vuelve a leer ambas particiones y compara todas las entidades
y sus frecuencias. Solo después escribe, en una única mutación de
`daily_news_metrics`, las métricas y `generation`. Esa fila es el punto de
publicación de una fecha. Un fallo previo deja visible la versión anterior; un
fallo de comunicación al publicar puede dejar visible la versión anterior o la
nueva, pero ambas están completas. Un reintento usa otro UUID y es seguro.

El dashboard, la reconciliación y la consulta CLI resuelven la generación activa
y leen una versión fija. Las fechas anteriores a la migración, con generación
nula, siguen leyendo las tablas originales. Los dos comandos históricos
`aggregate_daily` y `aggregate_entities` ahora publican el conjunto completo de
KPIs; el DAG invoca el agregador una sola vez.

## Actualizar un entorno existente

Con las variables de conexión cargadas, ejecutar:

```bash
python -m scripts.bootstrap_databases --database cassandra
python -m src.transformation.aggregate_daily
```

El bootstrap añade las tablas y, si falta, la columna UUID; no elimina datos.
El segundo comando migra todas las fechas MongoDB, una por una, manteniendo los
agregados anteriores disponibles hasta publicar cada nueva versión.

## Prueba de fallo y reintento

Elegir una fecha ya migrada y reconciliada en las tres bases:

```bash
python -m scripts.verify_cassandra_recovery --date 20261027
```

La demostración escribe 25 filas reales de una nueva versión e interrumpe la
etapa. Comprueba que el historial queda `failed`, que no existe reporte de éxito
y que todos los indicadores visibles permanecen idénticos. Repite la etapa con
el mismo identificador de ejecución, reconcilia las tres bases y comprueba el
estado `completed` y un UUID nuevo. Guarda la evidencia en
`docs/cassandra_recovery_verification.json`.

Desde Airflow, ejecutar estos módulos con el prefijo Compose de la guía
[Airflow local](airflow_local.md); sus clientes usan los nombres internos de los
servicios y los mismos archivos compartidos.

## Límites

La publicación corresponde a una fecha Cassandra; no constituye una transacción
entre fechas ni entre las tres bases. Se mantiene el contrato de archivos diarios
inmutables. Se requiere un único escritor por fecha; el DAG limita las ejecuciones activas
a una. No ejecutar la CLI sobre la misma fecha mientras el DAG la publica.

Las versiones anteriores, las tablas originales y los intentos incompletos se
conservan deliberadamente para permitir lectores que ya tomaron un UUID y para
inspección. Su limpieza con un período de retención queda pendiente; no debe
borrarse una versión que un lector todavía pueda estar usando. La caché del
dashboard puede mostrar una versión completa anterior durante hasta 60 segundos.
El despliegue local sigue usando un nodo y factor de replicación 1: esta mejora
protege contra cargas parciales, no contra la pérdida de ese nodo.
