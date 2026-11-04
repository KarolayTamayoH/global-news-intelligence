# Plan de cierre — Global News Intelligence

Revisión: 3 de noviembre de 2026. Entrega: 17 de noviembre.

Se revisaron todos los documentos del repositorio, los scripts y esquemas. Se recalcularon los cinco JSONL: 323.202 registros; identificadores únicos por archivo. En la revisión inicial no se consultaron bases en vivo ni Composer; la verificación del stack nuevo se registra en el avance de la segunda etapa. El detalle técnico y los modelos están en `informe.tex`.

| Fechas propuestas | Prioridad y trabajo | Criterio de cierre |
|---|---|---|
| 3–4 nov. | P0: unificar cabecera entre DAG y validador; corregir verificación Neo4j; corregir leyenda y dependencias visuales del dashboard | ZIP válido pasa ambos validadores; conteos reales del grafo comprobados para fechas con datos; vistas independientes |
| 4–6 nov. | P0: dependencias, Compose, configuración por entorno, índices y bootstrap | Arranque documentado desde otro equipo y carga de una partición |
| 6–10 nov. | P0: conectividad Composer–bases, archivos compartidos, tareas por fecha, DAG completo y schedule | Ejecución y reejecución programables con conteos reconciliados y sin duplicados |
| 10–12 nov. | P1: vistas MongoDB/Neo4j y scripts CRUD aislados para las tres bases | Tres conexiones visibles y CRUD demostrado con limpieza de datos de prueba |
| 12–14 nov. | P1: histórico Neo4j, cobertura de aristas y recuperación de agregados | Integridad por fecha y comportamiento tras fallo comprobados |
| 14–16 nov. | P1: capturas reales, informe final, evidencias y video grupal | PDF revisado, código reproducible y video de máximo 20–25 min con todos los integrantes |
| 17 nov. | Entrega y revisión final | Archivos y enlaces accesibles |

## Avance de la primera etapa — 3 de noviembre

Implementado:

- Validador compartido por el DAG y la ingesta local: cabecera exacta, once columnas, calendario, partición, NUMARTS, un CSV esperado y ZIP/CRC.
- Fecha de ejecución estable basada en fecha lógica UTC; si no existe, se exige `target_date` manual.
- Conteo almacenado en Neo4j comprobado también para cargas con datos, antes de escribir `completed`.
- Leyenda de temas corregida; otras vistas independientes de temas; tono nulo y variación con base cero muestran `N/D`.
- Diez pruebas de regresión con ZIP sintético, clientes Neo4j/MongoDB simulados y Streamlit AppTest.

Verificación local:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m src.validation.validate_gkg data/raw/20261027.gkg.csv.zip
```

La partición real devuelve 84.723 registros válidos. No se ejecutaron cargas sobre las bases ni se desplegó Composer. Airflow y Pendulum no están instalados localmente; las pruebas del DAG ejecutan únicamente sus cuerpos Python, con descargas simuladas. La importación del DAG y su ejecución en el scheduler siguen pendientes.

El DAG importa `src.validation.validate_gkg`: el despliegue debe incluir el paquete `src` en el PYTHONPATH del trabajador o instalar el proyecto. No basta subir solo el archivo del DAG.

## Segunda etapa — configuración reproducible

Implementado: `requirements.txt` y snapshot `requirements-lock.txt`; `compose.yaml` con tres servicios, volúmenes y healthchecks; `.env.example`; `src/config.py`; esquema MongoDB e índices; comando `python -m scripts.bootstrap_databases`; guía en [ejecucion_local.md](ejecucion_local.md).

Las cargas, agregaciones, dashboard y consultas de Cassandra usan la configuración central. Los agregadores permiten `--date YYYYMMDD`; las rutas de descarga y transformación se resuelven desde la raíz configurable. Se añadieron pruebas de configuración, bootstrap y protección de particiones vacías: 15 pruebas locales aprobadas. `pip check` no detectó dependencias incompatibles y Compose valida sin imprimir credenciales.

Verificación real completada en el nuevo stack: tres contenedores saludables; bootstrap repetido; 84.723 documentos de 20261027 cargados en MongoDB y 84.723 nodos GKGRecord en Neo4j. Cassandra coincide con MongoDB para 8.817 temas, 66.254 organizaciones y tono medio −0,6621133004352675. Neo4j contiene 707.104 relaciones HAS_THEME y 239.232 MENTIONS_ORG, según el límite actual de diez entradas por lista.

Evidencia guardada en [verificacion_local.json](verificacion_local.json). El comando `python -m scripts.verify_partition --date 20261027` reproduce la reconciliación sin modificar datos. El nuevo stack contiene solo esta partición; los 323.202 registros del informe corresponden a los cinco JSONL locales. Las bases anteriores no se adoptaron ni se borraron. Los servicios se dejan activos con volúmenes persistentes.

El bloque local está implementado y verificado. La instalación en una segunda máquina y la integración Airflow siguen pendientes.

Siguiente etapa: integrar todas las tareas del DAG y resolver despliegue/conectividad en Composer.

## Hallazgos iniciales que determinan el orden (previos a las correcciones)

- El DAG sí existe, pero tiene dos tareas y `schedule=None`. No integra las cargas. La cabecera real es interpretada como datos y provoca rechazo.
- El validador local espera cabecera exacta; el README describe erróneamente un archivo sin encabezado.
- En Neo4j la consulta de conteo almacenado está dentro de `if expected == 0`; el caso normal no se verifica. El grafo limita cada lista a diez entradas antes de deduplicar.
- El selector de fechas sí está implementado. La leyenda de temas muestra la última fecha y otras vistas dependen indebidamente de que existan temas.
- El dashboard consulta solo Cassandra. Faltan MongoDB y Neo4j.
- No hay manifiesto de dependencias ni Compose versionado; `tests/` está vacío. Hay esquemas CQL y Cypher, pero no creación explícita de índices o validación de esquema MongoDB.
- SHA-256 usa archivo y posición de fila. `$setOnInsert` evita duplicados al repetir el mismo archivo, pero no actualiza documentos existentes.
- La ventana incremental selecciona los últimos N archivos; no garantiza recuperar huecos más antiguos. Los agregadores recorren todas las fechas.
- DELETE seguido de INSERT en Cassandra permite lecturas parciales; los rankings leen y ordenan la partición completa en Python.

## Verificación y entrega documental

El informe conserva las once secciones solicitadas y agrega estado de cumplimiento y plan dentro de conclusiones. Los ejemplos CRUD son propuestas sin ejecutar. Las cifras de Neo4j y versiones del README se identifican como declaradas, sin atribuirles verificación actual. Las capturas se incorporan cuando existan en `docs/capturas/`; no se fabricaron evidencias.

Compilar desde la raíz (dos pasadas):

```bash
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
```

El documento incluye los esquemas del repositorio mediante rutas relativas. El logo es opcional en `figs/utec_logo.jpg`.
