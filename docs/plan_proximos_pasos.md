# Plan de cierre — Global News Intelligence

Actualización: 8 de noviembre de 2026. Entrega del curso: 17 de noviembre de 2026.

La entrega utiliza Airflow y las tres bases en Docker, archivos compartidos en `data/` y Streamlit en el Mac. La configuración vigente está en `deploy/local.json`.

## Avance comprobado

| Componente | Estado y evidencia |
|---|---|
| Datos | 403.941 registros reconciliados en seis fechas: 20261023–20261027 y 20261106 |
| Validación | Cabecera, once columnas, calendario, fecha de partición, NUMARTS y ZIP/CRC |
| MongoDB | Carga idempotente, esquema, índices e historiales de ingesta y pipeline |
| Cassandra | KPIs versionados; seis fechas migradas y reconciliadas; fallo parcial y reintento real verificados |
| Neo4j | Seis fechas reconciliadas con MongoDB; límite de diez entradas por lista conservado |
| DAG | Ocho tareas; dos ejecuciones completas locales con conteos idénticos y sin nuevos documentos al repetir |
| Programación | DAG activado; ejecución scheduled exitosa con ocho tareas y 80.739 registros de 20261106 reconciliados |
| Dashboard | Tres vistas conectadas, seis KPIs, filtros de documentos, paginación y grafo acotado |
| CRUD | Creación, consulta, actualización y eliminación verificadas en las tres bases; limpieza de UUID de prueba |
| Pruebas | 34 pruebas automatizadas, comprobación con bases reales y navegador sin errores JavaScript |
| Informe | Fuente LaTeX, PDF compilado, diagrama y seis capturas reales |

Los cinco JSONL locales suman 323.202 registros; el scheduler añadió 80.739 del 6 de noviembre. El total de las seis fechas en las bases es 403.941; evidencia en `historical_verification.json`. Un registro GKG no equivale a un artículo único. Las relaciones Neo4j reflejan solo las primeras diez entradas por lista antes de deduplicar.

## Próximos pasos

1. **Ejecución programada comprobada.** Evidencia en `airflow_scheduled_verification.json`; el DAG permanece activo con cron diario. El Mac y Docker deben permanecer activos y las descargas nuevas necesitan Internet.
2. **Histórico cargado y reconciliado.** Las cuatro cargas históricas terminaron con ocho tareas exitosas por ejecución. Se verificaron las seis fechas en las tres bases. Queda actualizar capturas e informe para mostrar el histórico actual.
3. **Recuperación Cassandra comprobada.** Fallo controlado tras 25 escrituras reales sin cambiar los KPIs visibles; reintento de la misma etapa y ejecución con estado final `completed`. Quedan recuperación de otras etapas, retención de versiones, medición de rendimiento, rankings en Python y cobertura del grafo.
4. **Cerrar la reproducibilidad.** Ejecutar el arranque en un segundo equipo, comprobar versiones, rutas con espacios, persistencia y comandos de inicialización.
5. **Preparar la exposición.** Grabar un video de máximo 20–25 minutos con todos los integrantes. Mostrar arquitectura, dataset, los tres modelos, CRUD, DAG, seis KPIs y dashboard.
6. **Revisar y entregar.** Antes del 17 de noviembre, comprobar informe PDF, código, scripts de creación, DAG, dashboard, video y evaluación de pares conforme a las instrucciones.

## Criterios de aceptación

| Pendiente | Criterio de cierre |
|---|---|
| Scheduler: cerrado | Ejecución scheduled, ocho tareas exitosas y reconciliación final guardadas en `airflow_scheduled_verification.json` |
| Histórico: cerrado | Seis fechas y 403.941 registros reconciliados; evidencia en `historical_verification.json` |
| Recuperación Cassandra: cerrada | Fallo parcial conserva la generación publicada y el reintento recupera el estado esperado; `cassandra_recovery_verification.json` |
| Reproducibilidad | Otra máquina inicia el stack y procesa una partición siguiendo la guía |
| Entrega | PDF, fuentes, evidencias y video accesibles y coherentes con el estado real |

## Evidencias y documentación

- [Ejecución local](ejecucion_local.md).
- [Airflow local](airflow_local.md).
- [Ejecución programada](airflow_scheduled_verification.json) e [histórico reconciliado](historical_verification.json).
- [Primera ejecución del DAG](airflow_verification_first.json) y [repetición](airflow_verification_repeat.json).
- [Reconciliación de las bases](verificacion_local.json).
- [Salud de Airflow y lectura de artefactos locales](local_environment_verification.json).
- [Dashboard real](dashboard_verification.json).
- [Recuperación Cassandra](cassandra_recovery_verification.json) y [seis versiones reconciliadas](cassandra_snapshot_verification.json).
- [CRUD y limpieza](crud_verification.json).
- [Capturas del navegador](capturas/browser_verification.json).

Compilar el informe desde la raíz, con dos pasadas:

```bash
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
```
