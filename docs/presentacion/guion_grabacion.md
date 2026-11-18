# Plan de grabación asíncrona

Video final estimado: **20:36** (objetivo 20 a 25 minutos). Cada integrante graba **un solo video** con un rango continuo de diapositivas; después se unen en el orden de la tabla. Los tiempos se calcularon a 2,3 palabras por segundo y las demostraciones en pantalla tienen tiempo fijo.

## Quién graba qué

| Video | Integrante | Rol acordado | Diapositivas | Tiempo disponible | Lugar en el video final | Archivo para grabar |
|---|---|---|---|---|---|---|
| 1 | Abel | Diagrama de arquitectura y orquestación con Airflow | 1 a 6 | 4:20 (máximo 4:35) | 0:00 - 4:20 | `por_integrante/Video_1_Abel_diapositivas_1-6.pptx` |
| 2 | Caroline | MongoDB: modelado y script de ingesta | 7 a 9 | 4:02 (máximo 4:17) | 4:20 - 8:22 | `por_integrante/Video_2_Caroline_diapositivas_7-9.pptx` |
| 3 | Mahir | Cassandra: modelado y script de ingesta | 10 a 13 | 4:06 (máximo 4:21) | 8:22 - 12:28 | `por_integrante/Video_3_Mayra_diapositivas_10-13.pptx` |
| 4 | Fabricio | Neo4j: modelado y script de ingesta | 14 a 17 | 4:03 (máximo 4:18) | 12:28 - 16:31 | `por_integrante/Video_4_Fabricio_diapositivas_14-17.pptx` |
| 5 | Alessandro | KPIs y dashboard | 18 a 21 | 4:05 (máximo 4:20) | 16:31 - 20:36 | `por_integrante/Video_5_Alessandro_diapositivas_18-21.pptx` |

Diferencia entre el que más y el que menos habla: 0:18. Cada uno queda entre 4:02 y 4:20.

## Cómo se respeta la división de tareas

- Abel: arquitectura y Airflow (diapositivas 4 a 6), más la apertura del video (portada, problema y pregunta, 1 a 3).
- Caroline: MongoDB (8 y 9), más los datos y la validación (7), que son la entrada de su script de ingesta.
- Mahir: Cassandra (10 y 11), más los resultados que se sirven desde Cassandra: volumen y tono (12 y 13).
- Fabricio: Neo4j (14 y 15), más el resultado del grafo (16) y la conciliación de las tres bases (17), que cierra la parte de bases de datos.
- Alessandro: KPIs y dashboard (18 y 19), más la discusión y las conclusiones (20 y 21), porque el dashboard integra todo lo anterior.

Cada uno defiende además la justificación de su propia base en la primera diapositiva de su rango, y cada uno hace su demostración en pantalla sobre la pestaña del dashboard que corresponde a su base.

## Antes de grabar

1. Cada uno abre solo su archivo de `por_integrante/` en modo presentación. Las notas del orador con el texto están en cada diapositiva y no se ven en la proyección.
2. Grabar la pantalla de la presentación y el micrófono, 1920 x 1080 o 1280 x 720, sin ventanas ni notificaciones encima.
3. Empezar cada video con una pausa de 2 segundos y terminar con otra pausa de 2 segundos, para poder cortar y unir sin que se pisen las voces.
4. Las demostraciones en pantalla (Caroline, Mahir, Fabricio y Alessandro) necesitan el dashboard abierto con las seis fechas cargadas. Se levanta con `docker compose --env-file .env up -d --wait mongodb cassandra neo4j` y luego `streamlit run dashboard/app.py`. En la diapositiva con demostración, grabar la ventana del navegador durante el tiempo fijado y volver a la presentación.
5. Cada video termina con la frase de traspaso que figura en el guion, salvo el último.
6. Si te pasas más de 15 segundos del tiempo asignado, recorta las últimas frases de tu intervención más larga, sin quitar la frase de traspaso.

## Orden de unión

1. Video 1: Abel (diapositivas 1 a 6), 4:20.
2. Video 2: Caroline (diapositivas 7 a 9), 4:02.
3. Video 3: Mahir (diapositivas 10 a 13), 4:06.
4. Video 4: Fabricio (diapositivas 14 a 17), 4:03.
5. Video 5: Alessandro (diapositivas 18 a 21), 4:05.

La diapositiva final (conclusiones) debe quedar en pantalla durante las preguntas, no se agrega una de agradecimiento después.

## Video 1: Abel, diapositivas 1 a 6

Tiempo total: 4:20. Rol: Diagrama de arquitectura y orquestación con Airflow. Archivo: `por_integrante/Video_1_Abel_diapositivas_1-6.pptx`. Demostración en pantalla: Ninguna.

### Diapositiva 1: Portada

⏱ en tu video 0:00 - 0:24 (24 s) · en el video final 0:00 - 0:24

> Hola, somos el equipo de Global News Intelligence. Presentaremos un pipeline que lleva noticias de GDELT a tres bases de datos y a un dashboard. Somos cinco. Yo soy Abel, a cargo de la arquitectura y de Airflow. Caroline presenta MongoDB, Mahir presenta Cassandra, Fabricio presenta Neo4j y Alessandro presenta los KPIs y el dashboard.

### Diapositiva 2: Motivación

⏱ en tu video 0:24 - 1:08 (44 s) · en el video final 0:24 - 1:08

> Empecemos por el problema. GDELT publica cada día un archivo con cientos de miles de registros sobre noticias del mundo. En nuestra carga, del 23 de octubre al 6 de noviembre, llegaron entre cuarenta mil y ochenta y cinco mil registros por día, y sumamos cuatrocientos tres mil novecientos cuarenta y uno en seis fechas. Ese mismo dato se necesita para tres usos distintos. Primero, conservar el original sin perder nada. Segundo, responder indicadores diarios rápido. Y tercero, explorar qué temas y organizaciones aparecen juntos. Una sola base de datos no resuelve bien las tres cosas, y de ahí nace el proyecto.

### Diapositiva 3: Pregunta

⏱ en tu video 1:08 - 1:45 (37 s) · en el video final 1:08 - 1:45

> Nuestra pregunta tiene dos partes. La primera es de modelado: qué base de datos conviene a cada tipo de dato de GDELT y por qué. La segunda es de ingeniería: si un flujo de Airflow puede automatizar todo el camino y dejar las tres bases conciliadas cada día. Nuestro aporte es un pipeline de extremo a extremo con seis KPIs y un dashboard que consulta las tres bases. Para responder, construimos primero el modelo de cada base y luego el flujo que las alimenta.

### Diapositiva 4: Arquitectura

⏱ en tu video 1:45 - 2:37 (52 s) · en el video final 1:45 - 2:37

> Esta es la arquitectura. Todo parte de GDELT, que entrega los archivos diarios. Apache Airflow orquesta el flujo con un DAG de ocho tareas. Primero los datos llegan a MongoDB, que es nuestra fuente de verdad. Desde MongoDB se alimentan en paralelo Cassandra, que guarda los KPIs por fecha, y Neo4j, que guarda las relaciones. Finalmente, el dashboard de Streamlit consulta las tres bases. Todo corre en contenedores con Docker Compose: MongoDB 8, Cassandra 5, Neo4j 5.26 y Airflow 2.11. Quiero resaltar dos decisiones. MongoDB va primero, así que cualquier fallo posterior se repara volviendo a leer los documentos originales. Y Cassandra y Neo4j leen desde MongoDB, lo que garantiza que las tres bases parten del mismo conjunto de registros.

### Diapositiva 5: Justificación

⏱ en tu video 2:37 - 3:17 (40 s) · en el video final 2:37 - 3:17

> Esta tabla resume la justificación técnica de dónde vive cada dato. El registro completo, con listas anidadas, va a MongoDB, porque un documento lo guarda tal como llega. Los KPIs diarios y los rankings van a Cassandra, porque se leen siempre por fecha y su modelo da lecturas rápidas y versiones de cada publicación. Y las relaciones entre registros, temas y organizaciones van a Neo4j, porque recorrer aristas es nativo y evita joins costosos. Si usáramos una sola base, perderíamos alguna de estas tres consultas. Mis compañeros lo detallan al presentar cada base.

### Diapositiva 6: DAG de Airflow

⏱ en tu video 3:17 - 4:20 (63 s) · en el video final 3:17 - 4:20

> El DAG de Airflow tiene ocho tareas y cubre las seis etapas exigidas. Primero select_partition fija la fecha. Luego extract descarga el archivo, validate comprueba su calidad y transform lo convierte a JSON por líneas. Después load_mongodb carga los documentos. A partir de ahí, aggregate_cassandra y load_neo4j corren en paralelo, y la última tarea, generate_indicators, concilia las tres bases y publica el reporte. Se ejecuta cada día a las seis de la mañana con una expresión cron, con dos reintentos de cinco minutos y sin catchup. Ya verificamos una ejecución programada real: la del seis de noviembre, con ochenta mil setecientos treinta y nueve registros conciliados. Cada tarea registra su estado en MongoDB, y como las cargas son idempotentes, volver a ejecutar una fecha no genera duplicados. Con esto el flujo queda automatizado. Le paso la palabra a Caroline, que empieza con los datos y MongoDB.

## Video 2: Caroline, diapositivas 7 a 9

Tiempo total: 4:02. Rol: MongoDB: modelado y script de ingesta. Archivo: `por_integrante/Video_2_Caroline_diapositivas_7-9.pptx`. Demostración en pantalla: Pestaña Documentos.

### Diapositiva 7: Datos

⏱ en tu video 0:00 - 1:04 (64 s) · en el video final 4:20 - 5:24

> Gracias, Abel. Soy Caroline y empiezo por los datos. Son el Global Knowledge Graph de GDELT: un archivo CSV tabulado dentro de un ZIP por cada día. Cada registro tiene once columnas, y tres son las que más usamos: THEMES, con la lista de temas; ORGANIZATIONS, con las organizaciones mencionadas; y TONE, con el tono del registro. Antes de cargar validamos el esquema exacto de las once columnas, que la fecha tenga formato válido y que el tono sea numérico. En la muestra de ochenta y tres mil registros no hubo ninguno mal formado. También vimos que algunos campos vienen vacíos con frecuencia, como las personas o los eventos asociados, por lo que el modelo tiene que tolerar campos faltantes sin fallar. Y como cada archivo trae los registros de su día, el volumen cambia mucho de una fecha a otra, algo que veremos en los resultados.

### Diapositiva 8: MongoDB: modelo

⏱ en tu video 1:04 - 2:00 (56 s) · en el video final 5:24 - 6:20

> Por qué MongoDB: el registro llega con listas de temas y organizaciones de longitud variable, y un documento las guarda tal como llegan, sin normalizarlas en varias tablas. El modelo tiene tres colecciones. gkg_records guarda un documento por registro, con las listas ya separadas. ingestion_history guarda un documento por archivo cargado, con su estado y sus conteos. Y pipeline_history guarda el estado de cada etapa del DAG, incluido el tipo de error si algo falla. La carga usa upsert por el identificador, con setOnInsert, así que repetir una fecha no duplica documentos: es idempotente. Además tenemos un validador JSON Schema, e índices por fecha, por archivo de origen y sobre la lista de temas, para que el dashboard filtre rápido por un tema exacto sin recorrer toda la colección.

### Diapositiva 9: MongoDB: ingesta y CRUD

⏱ en tu video 2:00 - 3:07 (67 s) · en el video final 6:20 - 7:27

> El script de ingesta lee el archivo transformado y carga los documentos por lotes. Al terminar, el pipeline comprueba que el conteo en MongoDB sea igual al conteo validado: para el seis de noviembre, ochenta mil setecientos treinta y nueve. En la captura vemos el explorador documental del dashboard, donde cada fila conserva el identificador, la cantidad de artículos asociados y las listas de temas y organizaciones tal como llegaron. También verificamos el CRUD completo: crear, leer, actualizar y borrar, eliminando los datos de prueba al final. Un detalle del modelo: el identificador de cada documento se deriva del archivo y de la fila, por eso volver a cargar la misma fecha reemplaza en lugar de duplicar. El historial de ingesta guarda cuántos registros se procesaron y cuándo terminó cada carga, lo que nos permite auditarlas. Y la etapa solo se da por completada si el conteo coincide con el del archivo validado.

⏱ en tu video 3:07 - 4:02 (55 s) · en el video final 7:27 - 8:22

> DEMOSTRACIÓN EN PANTALLA, pestaña Documentos del dashboard. Escribir una organización, por ejemplo reuters, y pulsar Consultar documentos. Decir: aquí MongoDB devuelve los registros tal como llegaron. Abrir un registro en Documento completo y mostrar el JSON. Cerrar diciendo: le paso la palabra a Mahir, que presenta Cassandra.

## Video 3: Mahir, diapositivas 10 a 13

Tiempo total: 4:06. Rol: Cassandra: modelado y script de ingesta. Archivo: `por_integrante/Video_3_Mayra_diapositivas_10-13.pptx`. Demostración en pantalla: Pestaña Indicadores.

### Diapositiva 10: Cassandra: modelo

⏱ en tu video 0:00 - 0:54 (54 s) · en el video final 8:22 - 9:16

> Gracias, Caroline. Soy Mahir y les presento Cassandra. Por qué Cassandra: los KPIs se leen siempre por fecha y se escriben una vez al día, y Cassandra está pensada para eso, con lecturas rápidas por partición. Por eso modelamos una tabla por consulta. daily_news_metrics guarda una fila por fecha con volumen, variación, diversidad y tono. Las tablas de temas y de organizaciones guardan los diez primeros de cada fecha. Para no mostrar nunca datos a medias, cada publicación escribe una versión nueva identificada con un UUID de generación: primero se escribe la versión, luego se verifican los conteos y solo al final se activa la generación. Usamos consistencia LOCAL_QUORUM, en un nodo con factor de replicación uno, suficiente para el entorno local del curso.

### Diapositiva 11: Cassandra: ingesta y recuperación

⏱ en tu video 0:54 - 1:32 (38 s) · en el video final 9:16 - 9:54

> El script de agregación calcula los KPIs desde MongoDB y los publica en Cassandra con ese protocolo de versiones. Gracias a las versiones, si una publicación falla a medias, el dashboard sigue leyendo la última generación completa y nunca ve números parciales. La captura muestra las tarjetas del dashboard servidas desde Cassandra: volumen, variación, diversidad temática y tono promedio del seis de noviembre. Además verificamos la recuperación: reiniciamos Cassandra y los KPIs publicados siguieron disponibles. El CRUD también quedó probado, con limpieza de los datos de prueba.

⏱ en tu video 1:32 - 2:17 (45 s) · en el video final 9:54 - 10:39

> DEMOSTRACIÓN EN PANTALLA, pestaña Indicadores. Cambiar la fecha del selector a 24/10/2026: el volumen baja a 47 019 y la variación a menos 40,7 por ciento. Volver a 06/11/2026. Decir: al cambiar la fecha, todo se recalcula leyendo Cassandra por partición de fecha.

### Diapositiva 12: Resultado: volumen

⏱ en tu video 2:17 - 3:07 (50 s) · en el video final 10:39 - 11:29

> Con los KPIs publicados, veamos los resultados. El primero es el volumen, el KPI uno, servido desde Cassandra. El 23 de octubre hay setenta y nueve mil trescientos cuarenta y nueve registros. El sábado 24 baja a cuarenta y siete mil diecinueve y el domingo 25 a cuarenta mil doscientos veintiocho, es decir, cerca de un cuarenta y nueve por ciento menos que el 23. El lunes 26 se recupera a setenta y un mil ochocientos ochenta y tres y el 27 llega a ochenta y cuatro mil setecientos veintitrés. Es un patrón semanal esperable: se publican menos noticias el fin de semana. Estos conteos coinciden con los de los documentos guardados en MongoDB.

### Diapositiva 13: Resultado: tono

⏱ en tu video 3:07 - 4:06 (59 s) · en el video final 11:29 - 12:28

> El segundo resultado es el tono promedio. Es negativo en las seis fechas, entre menos cero coma sesenta y seis y menos uno coma doce. El mínimo, menos uno coma doce, coincide con el domingo 25, justo el día de menor volumen. Una lectura posible es que con pocos registros cada noticia negativa pesa más en el promedio. Es una hipótesis que no probamos, pero el patrón es claro. Recuerden que el tono de GDELT va aproximadamente de menos diez a más diez, así que todos nuestros días están en el rango ligeramente negativo. Esto también ilustra por qué la variación se calcula frente a la fecha anterior disponible y no frente al día calendario previo: el seis de noviembre se compara con el veintisiete de octubre. Le paso la palabra a Fabricio, que presenta Neo4j.

## Video 4: Fabricio, diapositivas 14 a 17

Tiempo total: 4:03. Rol: Neo4j: modelado y script de ingesta. Archivo: `por_integrante/Video_4_Fabricio_diapositivas_14-17.pptx`. Demostración en pantalla: Pestaña Relaciones.

### Diapositiva 14: Neo4j: modelo

⏱ en tu video 0:00 - 1:03 (63 s) · en el video final 12:28 - 13:31

> Gracias, Mahir. Soy Fabricio y les presento Neo4j. Por qué Neo4j: la pregunta de qué temas y organizaciones aparecen juntos es una pregunta de relaciones, y en un grafo las relaciones son datos de primera clase. El modelo tiene tres tipos de nodos: GKGRecord, para cada registro; Theme, para cada tema; y Organization, para cada organización. Y dos relaciones: HAS_THEME, del registro a sus temas, y MENTIONS_ORG, del registro a las organizaciones que menciona. Para saber qué temas aparecen junto a una organización basta recorrer dos saltos desde el nodo, algo que en un modelo relacional exigiría varios joins sobre tablas grandes. Creamos restricciones de unicidad, y para controlar el tamaño enlazamos las diez primeras entidades de cada lista. Entre las seis fechas suman unos tres coma cuatro millones de aristas de temas y uno coma uno de organizaciones, sobre cuatrocientos tres mil nodos de registro.

### Diapositiva 15: Neo4j: ingesta y CRUD

⏱ en tu video 1:03 - 1:52 (49 s) · en el video final 13:31 - 14:20

> El script carga el grafo con MERGE en lotes de cien, de modo que repetir una fecha no duplica nodos ni relaciones. Gracias a eso podemos hacer preguntas de red. La captura es del dashboard: los pares de organizaciones que más coinciden en los registros. El par más frecuente es oval office y white house, con ochocientos cinco registros en común. En Neo4j también probamos el CRUD, incluyendo crear y borrar una relación. Antes de cargar, el script asegura las restricciones de unicidad y luego procesa los registros del día leyéndolos desde MongoDB. Como usa MERGE, es seguro reejecutarlo, y el pipeline lo invoca justamente para reparar nodos ausentes sin duplicar los existentes.

⏱ en tu video 1:52 - 2:32 (40 s) · en el video final 14:20 - 15:00

> DEMOSTRACIÓN EN PANTALLA, pestaña Relaciones. Mostrar las tarjetas de registros y relaciones, bajar a Actores que aparecen juntos y señalar el par oval office y white house. Decir: esto lo responde Neo4j recorriendo aristas, sin joins.

### Diapositiva 16: Neo4j: resultado

⏱ en tu video 2:32 - 3:13 (41 s) · en el video final 15:00 - 15:41

> El grafo también nos permite medir qué tan concentrada está la agenda. El seis de noviembre hay sesenta y seis mil trescientas veinte entidades únicas. Las diez organizaciones más citadas acumulan solo el once por ciento de las menciones, y el setenta por ciento de las organizaciones se menciona una sola vez: es una agenda fragmentada, con una cola larga de actores. Además, cada registro enlaza en promedio once coma tres temas y organizaciones, lo que da contexto a cada noticia. Por eso el dashboard permite explorar las conexiones de las veinticinco entidades más mencionadas.

### Diapositiva 17: Resultado: conciliación

⏱ en tu video 3:13 - 4:03 (50 s) · en el video final 15:41 - 16:31

> Para cerrar las bases, la conciliación. La última tarea del DAG compara, para cada fecha, los registros en MongoDB, Cassandra y Neo4j, y deben coincidir. La tabla muestra que coinciden en las seis fechas: la diferencia es cero, y suman cuatrocientos tres mil novecientos cuarenta y uno registros. Si alguna base no coincidiera, la tarea fallaría y el DAG no se marcaría como completo. Esto nos permite afirmar que el pipeline funciona de extremo a extremo y no solo cada pieza por separado. Cada corrida deja ese reporte en un archivo de indicadores y el estado de cada etapa en el historial del pipeline. Le paso la palabra a Alessandro, con los KPIs y el dashboard.

## Video 5: Alessandro, diapositivas 18 a 21

Tiempo total: 4:05. Rol: KPIs y dashboard. Archivo: `por_integrante/Video_5_Alessandro_diapositivas_18-21.pptx`. Demostración en pantalla: Pestaña Panorama.

### Diapositiva 18: KPIs

⏱ en tu video 0:00 - 1:09 (69 s) · en el video final 16:31 - 17:40

> Gracias, Fabricio. Soy Alessandro y presento los KPIs y el dashboard. Implementamos seis KPIs, y el mínimo pedido era cinco. El uno es el volumen diario. El dos es la variación diaria frente a la fecha disponible anterior. El tres es la frecuencia de temas, con los diez más frecuentes. El cuatro es la diversidad temática, cuántos códigos distintos aparecen. El cinco es el tono promedio. Y el seis son las organizaciones más mencionadas. Los valores del seis de noviembre son: ochenta mil setecientos treinta y nueve registros, una variación de menos cuatro coma siete por ciento, un tema líder con sesenta y siete mil trescientos cuarenta y siete registros, ocho mil seiscientos veintiséis temas distintos, un tono de menos cero coma setenta y seis, y united states como organización líder, con siete mil quinientas cincuenta y siete menciones. Todos se calculan una vez por fecha, durante la tarea de agregación, y las fórmulas completas están en el informe.

### Diapositiva 19: Dashboard: Panorama e Indicadores

⏱ en tu video 1:09 - 1:56 (47 s) · en el video final 17:40 - 18:27

> El dashboard lo hicimos en Streamlit y consulta las tres bases, con cuatro pestañas. Panorama resume la fecha: cuatrocientos tres mil novecientos cuarenta y uno registros analizados, seis fechas cargadas, ochenta mil setecientos treinta y nueve registros el seis de noviembre y tres de tres bases conectadas. Indicadores muestra los seis KPIs servidos desde Cassandra; aquí vemos el top diez de temas, con TAX_FNCACT presente en el ochenta y tres coma cuatro por ciento de los registros. Documentos consulta MongoDB y Relaciones consulta Neo4j, como mostraron Caroline y Fabricio. Con las cuatro pestañas el dashboard cumple el requisito de conectar las tres bases en una sola interfaz.

⏱ en tu video 1:56 - 2:41 (45 s) · en el video final 18:27 - 19:12

> DEMOSTRACIÓN EN PANTALLA, pestaña Panorama. Mostrar las cifras y el diagrama de las ocho tareas, cambiar la fecha del selector y señalar que las cuatro pestañas se actualizan. Decir: ninguna pestaña calcula nada por su cuenta, todo viene de las bases.

### Diapositiva 20: Discusión

⏱ en tu video 2:41 - 3:31 (50 s) · en el video final 19:12 - 20:02

> Como interpretación, cada base cubre una consulta propia que las otras no resuelven bien, y la conciliación confirma que el pipeline las mantiene consistentes. La persistencia políglota tiene sentido cuando los patrones de acceso son distintos, y su costo es operativo: hay tres sistemas que mantener, por eso el orquestador y la conciliación son piezas centrales. También debemos declarar los límites. Solo cargamos seis fechas, Cassandra corre en un solo nodo con factor de replicación uno, y el grafo se limita a diez entidades por lista. Son decisiones del entorno local del curso, no de la arquitectura. Como trabajo futuro, nos interesa cargar más fechas, escalar Cassandra a varios nodos y agregar indicadores de grafo.

### Diapositiva 21: Conclusiones

⏱ en tu video 3:31 - 4:05 (34 s) · en el video final 20:02 - 20:36

> Para concluir. Uno, MongoDB conserva el registro original y su carga es idempotente. Dos, Cassandra sirve KPIs versionados y recuperables. Tres, Neo4j responde preguntas de relaciones sin joins. Cuatro, el DAG de Airflow automatiza las seis etapas y las tres bases concilian: cuatrocientos tres mil novecientos cuarenta y uno registros con diferencia cero. Y cinco, seis KPIs y un dashboard unen las tres bases. El código y las evidencias están en el repositorio. Quedamos atentos a preguntas y comentarios.
