# Arranque local reproducible

Ejecutar desde la raíz del repositorio. El entorno comprobado usa Python 3.14.6, Docker Desktop y Compose v2.37.1. Las dependencias directas están fijadas en `requirements.txt`; `requirements-lock.txt` registra también las dependencias transitivas del entorno local. La instalación en otra plataforma sigue requiriendo verificación. Airflow no forma parte del entorno local: Composer administra su propia versión y restricciones.

## 1. Entorno Python

```bash
python3 --version
# Usar Python 3.14.6 para reproducir el entorno comprobado.
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
```

Si ya existe `.venv`, activarlo sin recrearlo. Para trabajar con esta estructura, usar `python -m src...` y `python -m scripts...`, desde la raíz, en lugar de invocar archivos sueltos.

## 2. Configuración

Copiar `.env.example` a `.env` solamente si aún no existe; conservar cualquier archivo y contraseña existentes. Cambiar `NEO4J_PASSWORD` por una contraseña local de al menos ocho caracteres. El usuario inicial del contenedor Neo4j es `neo4j`.

```bash
cp -n .env.example .env
# Editar .env antes de continuar.
set -a
source .env
set +a
```

`.env` debe ser compatible con el shell: entrecomillar contraseñas que contengan espacios o caracteres especiales. Los scripts Python leen las variables exportadas; no cargan automáticamente `.env`. Compose sí lo lee para interpolar su configuración. No mostrar `docker compose config` completo al compartir logs: incluye la autenticación de Neo4j. Usar `docker compose config --quiet` para validar sin imprimirla.

`src/config.py` centraliza URI, puertos, nombres de bases y rutas. `GNI_DATA_DIR` admite rutas absolutas o relativas a la raíz del proyecto. Para cambiar un puerto, ajustar tanto el puerto publicado por Compose como el URI del cliente correspondiente. Las variables de tu shell prevalecen sobre `.env` al invocar Compose.

## 3. Bases de datos

```bash
docker compose config --quiet
docker compose up -d --wait --wait-timeout 600
python -m scripts.bootstrap_databases
```

Compose crea servicios llamados `mongodb`, `cassandra` y `neo4j` bajo el proyecto `global-news-intelligence`, con volúmenes nuevos propios. No adopta automáticamente contenedores ni datos anteriores. Si otro servicio ocupa 27018, 9043, 7475 o 7688, detenerlo de forma consciente o cambiar los puertos de esta configuración. No ejecutar ambos stacks sobre los mismos puertos.

Las imágenes predeterminadas son MongoDB 8.0, Cassandra 5.0 y Neo4j 5.26 Community. Son tags de serie, no digests inmutables; `MONGO_IMAGE`, `CASSANDRA_IMAGE` y `NEO4J_IMAGE` permiten fijar una compilación exacta. Los puertos se publican exclusivamente en 127.0.0.1 para la demostración local. MongoDB y Cassandra no tienen autenticación habilitada en este stack; su uso remoto exige otra configuración. Cassandra y Neo4j pueden tardar varios minutos en iniciar; `--wait` comprueba los healthchecks.

El bootstrap admite `--database mongodb`, `--database cassandra` o `--database neo4j`. Es repetible: aplica el validador MongoDB y crea índices, tablas y restricciones que falten. No elimina registros. En colecciones existentes, `collMod` aplica el contrato a escrituras posteriores; no certifica que los registros anteriores lo cumplan.

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
python -m scripts.verify_partition --date 20261027 --output docs/verificacion_local.json
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
python -m streamlit run dashboard/app.py
python -m unittest discover -s tests -v
```

Streamlit se abre en http://localhost:8501 y consulta Cassandra. Neo4j Browser está en http://localhost:7475. Los tests usan servicios simulados: no reemplazan una comprobación de integración con contenedores.

## Resultado comprobado el 3 de noviembre de 2026

Se inició el stack y se repitió el bootstrap. La partición 20261027 cargó 84.723 documentos y nodos; Cassandra coincide con MongoDB en volumen, tono y todos los conteos de 8.817 temas y 66.254 organizaciones. Se reconciliaron 707.104 relaciones temáticas y 239.232 organizacionales con el límite actual del grafo. La evidencia está en [verificacion_local.json](verificacion_local.json).

El stack nuevo usa volúmenes propios y contiene esta única fecha. Los cinco JSONL locales suman 323.202 registros. La verificación local no certifica instalación en otra máquina ni ejecución en Composer.

## Referencias técnicas

- [Docker: orden de arranque y healthchecks](https://docs.docker.com/compose/how-tos/startup-order/).
- [MongoDB: validación de esquema](https://www.mongodb.com/docs/manual/core/schema-validation/).
