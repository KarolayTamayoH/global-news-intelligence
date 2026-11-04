# Plan de cierre — Global News Intelligence

Corte: 3 de noviembre de 2026. Entrega del curso: 17 de noviembre de 2026.

La entrega utiliza Airflow y las tres bases en Docker, archivos compartidos en `data/` y Streamlit en el Mac. La configuración vigente está en `deploy/local.json`.

## Avance comprobado

| Componente | Estado y evidencia |
|---|---|
| Datos | Cinco JSONL locales suman 323.202 registros; el stack actual contiene 84.723 de 20261027 |
| Validación | Cabecera, once columnas, calendario, fecha de partición, NUMARTS y ZIP/CRC |
| MongoDB | Carga idempotente, esquema, índices e historiales de ingesta y pipeline |
| Cassandra | Métricas diarias y frecuencias de temas/organizaciones por fecha |
| Neo4j | 84.723 registros, 707.104 relaciones temáticas y 239.232 organizacionales reconciliados |
| DAG | Ocho tareas; dos ejecuciones completas locales con conteos idénticos y sin nuevos documentos al repetir |
| Programación | Cron 06:00 UTC / 01:00 Lima configurado; activación y ejecución observada pendientes |
| Dashboard | Tres vistas conectadas, seis KPIs, filtros de documentos, paginación y grafo acotado |
| CRUD | Creación, consulta, actualización y eliminación verificadas en las tres bases; limpieza de UUID de prueba |
| Pruebas | 28 pruebas automatizadas, comprobación con bases reales y navegador sin errores JavaScript |
| Informe | Fuente LaTeX, PDF compilado, diagrama y seis capturas reales |

No se equiparan los 323.202 registros de archivos con el conteo del stack actual. Un registro GKG no equivale a un artículo único. Las relaciones Neo4j reflejan solo las primeras diez entradas por lista antes de deduplicar.

## Próximos pasos

1. **Demostrar la ejecución programada.** Comprobar scheduler, activar el DAG y observar una ejecución disparada por su calendario. Guardar estado, fecha del intervalo, logs y conteos. El Mac y Docker deben permanecer activos y las descargas nuevas necesitan Internet. `dag.test()` no demuestra el disparo por calendario.
2. **Ampliar el histórico de forma coherente.** Cargar las particiones restantes en las tres bases y reconciliar cada fecha. Actualizar las capturas cuando el dashboard muestre varios días y una variación calculable.
3. **Verificar recuperación y rendimiento.** Probar reintentos y fallos parciales; revisar el reemplazo no atómico de particiones Cassandra, el ordenamiento de rankings en Python y la cobertura limitada del grafo.
4. **Cerrar la reproducibilidad.** Ejecutar el arranque en un segundo equipo, comprobar versiones, rutas con espacios, persistencia y comandos de inicialización.
5. **Preparar la exposición.** Grabar un video de máximo 20–25 minutos con todos los integrantes. Mostrar arquitectura, dataset, los tres modelos, CRUD, DAG, seis KPIs y dashboard.
6. **Revisar y entregar.** Antes del 17 de noviembre, comprobar informe PDF, código, scripts de creación, DAG, dashboard, video y evaluación de pares conforme a las instrucciones.

## Criterios de aceptación

| Pendiente | Criterio de cierre |
|---|---|
| Scheduler | Ejecución identificada como programada, ocho tareas exitosas y reconciliación final |
| Histórico | Conteos y agregados coincidentes en todas las fechas incorporadas |
| Recuperación | Un fallo no se marca como completo y el reintento recupera el estado esperado |
| Reproducibilidad | Otra máquina inicia el stack y procesa una partición siguiendo la guía |
| Entrega | PDF, fuentes, evidencias y video accesibles y coherentes con el estado real |

## Evidencias y documentación

- [Ejecución local](ejecucion_local.md).
- [Airflow local](airflow_local.md).
- [Primera ejecución del DAG](airflow_verification_first.json) y [repetición](airflow_verification_repeat.json).
- [Reconciliación de las bases](verificacion_local.json).
- [Salud de Airflow y lectura de artefactos locales](local_environment_verification.json).
- [Dashboard real](dashboard_verification.json).
- [CRUD y limpieza](crud_verification.json).
- [Capturas del navegador](capturas/browser_verification.json).

Compilar el informe desde la raíz, con dos pasadas:

```bash
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
```
