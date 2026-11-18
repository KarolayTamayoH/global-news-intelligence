# Arranque local reproducible

Ejecutar desde la raíz del repositorio. La entrega local usa Docker Desktop y Compose; un solo `compose.yaml` administra MongoDB, Cassandra, Neo4j, Airflow y Streamlit. El entorno Python local es opcional y se usa para scripts y pruebas, no para servir el dashboard.

## 1. Entorno Python

```bash
python3 --version
# Usar Python 3.14.6 para reproducir el entorno comprobado.
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Si ya existe `.venv`, activarlo sin recrearlo. Para trabajar con esta estructura, usar `python -m src...` y `python -m scripts...`, desde la raíz, en lugar de invocar archivos sueltos.

## 2. Configuración

Copiar `.env.example` a `.env` solamente si aún no existe; conservar cualquier configuración local. Neo4j no requiere contraseña en este stack local. `AIRFLOW_ADMIN_PASSWORD` configura únicamente el acceso a la interfaz de Airflow.

```bash
cp -n .env.example .env
# Editar .env antes de continuar.
set -a
source .env
set +a
```

Compose y `src/config.py` cargan `.env` automáticamente. Las variables presentes en el shell prevalecen. No mostrar `docker compose config` completo al compartir logs: incluye la autenticación de Neo4j. Usar `docker compose config --quiet` para validar sin imprimirla.

`src/config.py` centraliza URI, puertos, nombres de bases y rutas. `GNI_DATA_DIR` admite rutas absolutas o relativas a la raíz del proyecto. Para cambiar un puerto, ajustar tanto el puerto publicado por Compose como el URI del cliente correspondiente. Las variables de tu shell prevalecen sobre `.env` al invocar Compose.

## 3. Bases de datos

```bash
docker compose up -d --build --wait --wait-timeout 600
```

Compose crea `mongodb`, `cassandra`, `neo4j`, `airflow-db`, `airflow` y `dashboard` bajo el proyecto `global-news-intelligence`, con sus volúmenes. No adopta automáticamente contenedores ni datos anteriores. Si otro servicio ocupa 27018, 9043, 7475, 7688, 8080 o 8501, cambiar los puertos en `.env`.

Las versiones base de MongoDB 8.0, Cassandra 5.0 y Neo4j 5.26 Community se declaran en `docker/mongo/Dockerfile`, `docker/cassandra/Dockerfile` y `docker/neo4j/Dockerfile`. Los puertos se publican exclusivamente en 127.0.0.1 para la demostración local. MongoDB y Cassandra se utilizan sin autenticación adicional dentro de la red local de Docker. Cassandra y Neo4j pueden tardar varios minutos en iniciar; `--wait` comprueba los healthchecks.

Airflow ejecuta automáticamente `python -m scripts.bootstrap_databases` antes de iniciar el scheduler, tanto con volúmenes nuevos como en reinicios. El bootstrap admite `--database mongodb`, `--database cassandra` o `--database neo4j`. Es repetible: aplica el validador MongoDB y crea índices, tablas y restricciones que falten. No elimina registros. En colecciones existentes, `collMod` aplica el contrato a escrituras posteriores; no certifica que los registros anteriores lo cumplan.

Comprobar estado y logs:

```bash
docker compose ps
docker compose logs --tail 40 cassandra
```

Para detener y conservar volúmenes:

```bash
docker compose down
```

## 4. Cargar una partición histórica

Con el ZIP local disponible:

```bash
python -m src.validation.validate_gkg data/raw/20261027.gkg.csv.zip
python -m src.transformation.transform_gkg data/raw/20261027.gkg.csv.zip
python -m src.ingestion.load_mongodb data/processed/20261027.jsonl
python -m src.transformation.aggregate_daily --date 20261027
python -m src.transformation.aggregate_entities --date 20261027
python -m src.ingestion.load_neo4j --date 20261027
python -m scripts.verify_partition --date 20261027 --output docs/data-utils/verificacion_local.json
```

Si se cambia `GNI_DATA_DIR`, sustituir los argumentos de archivo por esa ruta. El transformador escribe siempre dentro del directorio procesado configurado. Los agregadores aceptan `--date YYYYMMDD`; sin ese argumento recorren todas las fechas almacenadas. Si la fecha explícita no contiene documentos, fallan antes de escribir agregados. `verify_partition` contrasta registros, todos los conteos de entidades y tono Cassandra, además de los conteos de nodos y relaciones Neo4j según el límite actual de diez entidades; no comprueba la identidad de cada arista.

Si no existe el ZIP local, descargar la partición explícita (requiere Internet):

```bash
python -c 'from src.ingestion.download_gdelt import download_file; download_file("20261027.gkg.csv.zip")'
```

La carga directa a MongoDB no escribe `ingestion_history`; ese historial pertenece al ejecutor incremental. La idempotencia documental usa identificadores estables y upsert. Neo4j omite fechas previamente marcadas completas; no usar esa omisión como evidencia de una nueva reconciliación. Los agregados Cassandra reemplazan las particiones de entidades con DELETE + INSERT, con una ventana de lectura parcial aún pendiente de resolver.

Para la ventana incremental disponible hacia MongoDB:

```bash
python -m src.ingestion.run_incremental --days 5
```

## 5. Dashboard y pruebas

```bash
docker compose up -d dashboard
python -m unittest discover -s tests -v
```

Streamlit se abre en http://localhost:8501 como servicio del mismo Compose y consulta Cassandra, MongoDB y Neo4j en tres vistas. El selector de fecha filtra rankings, documentos y relaciones; el explorador documental añade filtros y paginación y el grafo muestra una muestra limitada de conexiones. Neo4j Browser está en http://localhost:7475. Los tests usan servicios simulados: no reemplazan una comprobación de integración con contenedores.

## 6. Airflow local y demostración CRUD

Airflow se inicia junto con los otros servicios mediante `docker compose up -d`. Su interfaz está en http://localhost:8080. La contraseña web se configura con `AIRFLOW_ADMIN_PASSWORD`; la conexión interna a PostgreSQL no necesita una clave en este despliegue local. El DAG queda activo por defecto y programa la extracción a las 06:00 UTC (01:00 Lima), con `catchup=False`. El equipo y Docker deben permanecer activos para ejecutar la programación; las descargas nuevas necesitan Internet. Los archivos de GDELT se descargan a disco y se comparten mediante el volumen local.

Ejecutar CRUD en las tres bases:

```bash
python -m scripts.crud_demo --output docs/data-utils/crud_verification.json
```

Se usan `crud_demo` en MongoDB y Cassandra y nodos `CrudDemo` en Neo4j. Cada ejecución genera identificadores UUID y verifica creación, lectura, cambio de valor 1 a 2 y eliminación. Neo4j verifica además creación, actualización y eliminación de una relación. La limpieza final solo elimina esos identificadores, incluso si falla una comprobación. Las colecciones/tablas vacías de prueba se conservan para repetir la demostración.

Verificar aplicación y datos reales:

```bash
python -m scripts.verify_dashboard --date 20261027
python -m scripts.verify_partition --date 20261027 --output docs/data-utils/verificacion_local.json
```

La configuración vigente está en `deploy/local.json`. Los detalles de las ocho tareas y su programación están en [airflow_local.md](airflow_local.md).

## Resultado comprobado el 3 de noviembre de 2026

Se inició el stack y se repitió el bootstrap. La partición 20261027 cargó 84.723 documentos y nodos; Cassandra coincide con MongoDB en volumen, tono y todos los conteos de 8.817 temas y 66.254 organizaciones. Se reconciliaron 707.104 relaciones temáticas y 239.232 organizacionales con el límite actual del grafo. La evidencia está en [verificacion_local.json](verificacion_local.json).

El stack nuevo usa volúmenes propios y contiene esta única fecha. Los cinco JSONL locales suman 323.202 registros. La reproducción en una segunda máquina sigue pendiente.

## Referencias técnicas

- [Docker: orden de arranque y healthchecks](https://docs.docker.com/compose/how-tos/startup-order/).
- [MongoDB: validación de esquema](https://www.mongodb.com/docs/manual/core/schema-validation/).

## Dashboard y CRUD comprobados

Las tres vistas del dashboard se verificaron con bases reales y sin errores. La demostración CRUD completó creación, consulta, actualización y eliminación en las tres bases y limpió sus datos. Los conteos de los registros GKG y sus relaciones permanecieron intactos. Resultados: `docs/data-utils/dashboard_verification.json`, `docs/data-utils/crud_verification.json` y `docs/data-utils/verificacion_local.json`.

Se capturaron seis pantallas reales en Chrome. El script opcional `scripts/capture_dashboard.cjs` requiere Playwright y Chrome; esas herramientas de captura no son dependencias de la aplicación. En este equipo se ejecutó con Playwright instalado en `/tmp/gni-browser-tools`:

```bash
NODE_PATH=/tmp/gni-browser-tools/node_modules node scripts/capture_dashboard.cjs
```

Las capturas se guardan en `docs/capturas/` y se incluyen directamente en `informe.tex`. Las credenciales no se muestran en las capturas ni en los JSON.
