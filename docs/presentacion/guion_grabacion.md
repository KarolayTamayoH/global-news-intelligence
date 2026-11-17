# Guion de grabación

Duración estimada del video: **21:05** (objetivo 20 a 25 minutos). Cada intervención se calculó a 2,3 palabras por segundo; las demostraciones en vivo tienen tiempo fijo. Los mismos textos están en las notas del orador de `global_news_intelligence.pptx` (no se ven en la proyección).

## Tiempo por integrante

| Integrante | Rol acordado | Tiempo | Diapositivas |
|---|---|---|---|
| Abel | Diagrama de arquitectura y orquestación con Airflow | 3:59 | 1, 2, 5, 7, 21 |
| Caroline | MongoDB: modelado y script de ingesta | 4:24 | 1, 6, 8, 9, 15, 17, 19 |
| Mayra | Cassandra: modelado y script de ingesta | 4:20 | 1, 4, 6, 10, 11, 16, 20 |
| Fabricio | Neo4j: modelado y script de ingesta | 4:30 | 1, 3, 6, 12, 13, 19, 20, 21 |
| Alessandro | KPIs y dashboard | 3:52 | 1, 14, 18, 19, 21 |

Reparto: todos quedan entre 3:52 y 4:30. Los roles acordados se respetan en las diapositivas de su base de datos o componente. Para equilibrar, Abel abre la motivación, Fabricio plantea la pregunta, Mayra presenta el dataset y Caroline presenta los resultados de volumen y conciliación.

Cómo usarlo: cada uno lee su parte en voz alta en el orden indicado; el cronómetro marca el tiempo acumulado del video. Si graban por separado, cada uno graba sus segmentos y se unen en ese orden. Los textos entre «DEMOSTRACIÓN EN VIVO» son indicaciones para el que opera el dashboard.

## Guion por diapositiva

### Diapositiva 1: Portada

**ABEL** · 0:00 - 0:21 (21 s)

> Hola, somos el equipo de Global News Intelligence. Presentaremos un pipeline que lleva noticias de GDELT a tres bases de datos y a un dashboard. Yo soy Abel y me encargué del diagrama de arquitectura y de la orquestación con Airflow. Cada uno presentará la parte que construyó.

**CAROLINE** · 0:21 - 0:27 (6 s)

> Soy Caroline. Me encargué del modelado y del script de ingesta de MongoDB.

**MAYRA** · 0:27 - 0:33 (6 s)

> Soy Mayra. Me encargué del modelado y del script de ingesta de Cassandra.

**FABRICIO** · 0:33 - 0:39 (6 s)

> Soy Fabricio. Me encargué del modelado y del script de ingesta de Neo4j.

**ALESSANDRO** · 0:39 - 0:44 (5 s)

> Y yo soy Alessandro. Implementé los KPIs y el dashboard.

### Diapositiva 2: Motivación

**ABEL** · 0:44 - 1:55 (71 s)

> Empecemos por el problema. GDELT publica cada día un archivo con cientos de miles de registros sobre noticias del mundo. En nuestra carga, entre el 23 de octubre y el 6 de noviembre, llegaron entre cuarenta mil y ochenta y cinco mil registros por día, y sumamos cuatrocientos tres mil novecientos cuarenta y uno en seis fechas. Ese mismo dato se necesita para tres usos distintos. Primero, conservar el registro original sin perder nada. Segundo, responder indicadores diarios rápido. Y tercero, explorar qué temas y organizaciones aparecen juntos, que es una pregunta de relaciones. Una sola base de datos no resuelve bien las tres cosas, y de ahí nace el proyecto. Para darle contexto: el GKG, o Global Knowledge Graph, resume qué publicó la prensa mundial en cada fecha, con los temas tratados, las organizaciones mencionadas y el tono de la cobertura. Es un dato semiestructurado: tiene columnas fijas, pero con listas de longitud variable dentro de cada campo. Eso condiciona cómo lo guardamos.

### Diapositiva 3: Pregunta

**FABRICIO** · 1:55 - 2:50 (55 s)

> Con eso en mente, nuestra pregunta tiene dos partes. La primera es de modelado: qué base de datos conviene a cada tipo de dato de GDELT y por qué. La segunda es de ingeniería: si un flujo de Airflow puede automatizar todo el camino y dejar las tres bases conciliadas cada día. Nuestro aporte es un pipeline de extremo a extremo con seis KPIs y un dashboard que consulta las tres bases. Dicho de otra forma, no buscamos la mejor base en abstracto, sino asignar cada dato a la base que lo consulta mejor, y demostrar que el conjunto funciona de manera automática y reproducible, con evidencias verificables en el repositorio. Para responder, construimos primero el modelo de cada base y luego el flujo que las alimenta.

### Diapositiva 4: Datos

**MAYRA** · 2:50 - 3:58 (68 s)

> Los datos son el Global Knowledge Graph de GDELT, un archivo CSV tabulado dentro de un ZIP por cada día. Cada registro tiene once columnas. Tres de ellas son las que más usamos: THEMES, con la lista de temas; ORGANIZATIONS, con las organizaciones mencionadas; y TONE, con el tono del registro. Antes de cargar, validamos el esquema exacto de las once columnas, que la fecha tenga formato válido y que el tono sea numérico. En la muestra de ochenta y tres mil registros no hubo ninguno mal formado. Esta validación es la segunda etapa del pipeline. Un detalle importante es que cada archivo trae sus propios registros del día, así que el volumen cambia mucho de una fecha a otra; más adelante veremos ese efecto en los resultados. También es relevante que algunos campos vienen vacíos con frecuencia, como las personas o los eventos asociados, por lo que el modelo tiene que tolerar campos faltantes sin fallar.

### Diapositiva 5: Arquitectura

**ABEL** · 3:58 - 5:06 (68 s)

> Esta es la arquitectura. Todo parte de GDELT, que entrega los archivos diarios. Apache Airflow orquesta el flujo con un DAG de ocho tareas. Primero los datos llegan a MongoDB, que es nuestra fuente de verdad. Desde MongoDB se alimentan en paralelo Cassandra, que guarda los KPIs por fecha, y Neo4j, que guarda las relaciones. Finalmente, el dashboard de Streamlit consulta las tres bases. Todo corre en contenedores con Docker Compose: MongoDB 8, Cassandra 5, Neo4j 5.26 y Airflow 2.11. La idea central es que cada base recibe los datos que su modelo consulta mejor, y eso lo justifican mis compañeros en la siguiente diapositiva. Quiero resaltar dos decisiones. La primera es que MongoDB va primero: cualquier fallo posterior se puede reparar volviendo a leer los documentos originales. La segunda es que Cassandra y Neo4j no leen el archivo crudo, leen desde MongoDB, lo que garantiza que las tres bases parten del mismo conjunto de registros.

### Diapositiva 6: Justificación

**CAROLINE** · 5:06 - 5:25 (19 s)

> Empiezo yo con MongoDB. El registro completo de GKG, con listas anidadas y longitud variable, va a MongoDB porque un documento lo guarda tal como llega, con validador de esquema y carga idempotente mediante upsert. Eso evita normalizar las listas en varias tablas.

**MAYRA** · 5:25 - 5:44 (19 s)

> Los KPIs diarios y los rankings van a Cassandra. Se leen siempre por fecha, y su modelo de tablas por consulta nos da lecturas rápidas por partición, además de versiones de cada publicación. Así el dashboard no tiene que recalcular nada al consultar.

**FABRICIO** · 5:44 - 6:05 (21 s)

> Y las relaciones entre registros, temas y organizaciones van a Neo4j, porque recorrer aristas es nativo: preguntas como qué organizaciones aparecen juntas se resuelven sin joins costosos. Si usáramos una sola base, perderíamos alguna de estas tres consultas. Por eso decidimos usar las tres, cada una en su rol.

### Diapositiva 7: DAG de Airflow

**ABEL** · 6:05 - 7:17 (72 s)

> El DAG de Airflow tiene ocho tareas y cubre las seis etapas exigidas. Primero select_partition fija la fecha. Luego extract descarga el archivo, validate comprueba su calidad y transform lo convierte a JSON por líneas. Después load_mongodb carga los documentos. A partir de ahí, aggregate_cassandra y load_neo4j corren en paralelo, y la última tarea, generate_indicators, concilia las tres bases y publica el reporte. Se ejecuta cada día a las seis de la mañana con una expresión cron, con dos reintentos de cinco minutos y sin catchup. Ya verificamos una ejecución programada real: la del seis de noviembre, con ochenta mil setecientos treinta y nueve registros conciliados. En el apéndice C está el mismo diagrama tal como lo muestra el dashboard. Cada tarea registra su estado en la colección pipeline_history de MongoDB: si falla, se guarda el tipo de error y la etapa queda marcada como fallida, lo que facilita reintentar solo lo necesario. Como las cargas son idempotentes, volver a ejecutar una fecha no genera duplicados.

### Diapositiva 8: MongoDB: modelo

**CAROLINE** · 7:17 - 8:09 (52 s)

> En MongoDB hay tres colecciones. gkg_records guarda un documento por registro, con las listas de temas y organizaciones ya separadas. ingestion_history guarda un documento por archivo cargado, y pipeline_history guarda el estado de cada etapa del DAG. La carga usa upsert por el identificador, con setOnInsert, así que repetir una fecha no duplica documentos: es idempotente. Además tenemos un validador JSON Schema, e índices por fecha y por archivo de origen para que las consultas del dashboard sean rápidas. Elegimos este modelo porque el registro llega con listas de longitud variable, y un documento las representa de forma natural. Para el dashboard, el índice sobre la lista de temas permite filtrar por un tema exacto sin recorrer toda la colección.

### Diapositiva 9: MongoDB: ingesta y CRUD

**CAROLINE** · 8:09 - 8:54 (45 s)

> El script de ingesta lee el archivo transformado y carga los documentos por lotes. Al terminar, el pipeline comprueba que el conteo en MongoDB sea igual al conteo validado: para el seis de noviembre, ochenta mil setecientos treinta y nueve. A la izquierda vemos el explorador documental del dashboard, que consulta MongoDB con filtros por tema exacto o por organización. También verificamos el CRUD completo: crear, leer, actualizar y borrar, eliminando los datos de prueba al final. En el explorador se ve que cada fila conserva el identificador, la cantidad de artículos asociados, y las listas de temas y organizaciones tal como llegaron.

### Diapositiva 10: Cassandra: modelo

**MAYRA** · 8:54 - 9:50 (56 s)

> En Cassandra modelamos una tabla por consulta. daily_news_metrics guarda una fila por fecha con volumen, variación, diversidad y tono. Las tablas de temas y de organizaciones guardan los diez primeros de cada fecha. Para no mostrar nunca datos a medias, cada publicación escribe una versión nueva identificada con un UUID de generación. Primero se escribe la versión, luego se verifican los conteos y solo al final se activa la generación. Usamos consistencia LOCAL_QUORUM. Es un nodo con factor de replicación uno, suficiente para el entorno local del curso. Esto responde a la forma de trabajo de Cassandra: se diseña la tabla a partir de la consulta, no al revés. El dashboard siempre pregunta por una fecha, así que cada lectura va directa a su partición sin escanear nada.

### Diapositiva 11: Cassandra: ingesta y recuperación

**MAYRA** · 9:50 - 10:29 (39 s)

> El script de agregación calcula los KPIs desde MongoDB y los publica en Cassandra con ese protocolo de versiones. La captura muestra las tarjetas del dashboard servidas desde Cassandra: volumen, variación, diversidad temática y tono promedio del seis de noviembre. Además verificamos la recuperación: reiniciamos Cassandra y los KPIs publicados siguieron disponibles. El CRUD también quedó probado en esta base, con limpieza de los datos de prueba. Gracias a las versiones, si una publicación falla a medias, el dashboard sigue leyendo la última generación completa y nunca ve números parciales.

### Diapositiva 12: Neo4j: modelo

**FABRICIO** · 10:29 - 11:34 (65 s)

> En Neo4j el modelo tiene tres tipos de nodos: GKGRecord, para cada registro; Theme, para cada tema; y Organization, para cada organización. Y dos relaciones: HAS_THEME, del registro a sus temas, y MENTIONS_ORG, del registro a las organizaciones que menciona. Para controlar el tamaño del grafo enlazamos las diez primeras entidades de cada lista. Entre las seis fechas suman unos tres coma cuatro millones de aristas de temas y uno coma uno de organizaciones, unos cuatro millones y medio en total, sobre cuatrocientos tres mil nodos de registro. La ventaja del grafo es que las relaciones se guardan como datos de primera clase. Para saber qué temas aparecen en los mismos registros que una organización, basta recorrer dos saltos desde el nodo, algo que en un modelo relacional exigiría varios joins sobre tablas grandes. También creamos restricciones de unicidad para que cada tema y cada organización existan una sola vez.

### Diapositiva 13: Neo4j: ingesta y CRUD

**FABRICIO** · 11:34 - 12:22 (48 s)

> El script carga el grafo con MERGE en lotes de cien, de modo que repetir una fecha no duplica nodos ni relaciones. Gracias a eso podemos hacer preguntas de red. La captura es del dashboard: los pares de organizaciones que más coinciden en los registros. El par más frecuente es oval office y white house, con ochocientos cinco registros en común. En Neo4j también probamos el CRUD, incluyendo crear y borrar una relación. El dashboard también calcula la concentración de la agenda: por ejemplo, las diez organizaciones más citadas acumulan el once por ciento de las menciones, y el setenta por ciento de las organizaciones se menciona una sola vez.

### Diapositiva 14: KPIs

**ALESSANDRO** · 12:22 - 13:44 (82 s)

> Implementamos seis KPIs, y el mínimo pedido era cinco. El uno es el volumen diario: cuántos registros hay en la fecha. El dos es la variación diaria, el cambio porcentual frente a la fecha disponible anterior. El tres es la frecuencia de temas, con los diez más frecuentes. El cuatro es la diversidad temática, cuántos códigos de tema distintos aparecen. El cinco es el tono promedio. Y el seis son las organizaciones más mencionadas. Los valores del seis de noviembre son: ochenta mil setecientos treinta y nueve registros, una variación de menos cuatro coma siete por ciento, un tema líder con sesenta y siete mil trescientos cuarenta y siete registros, ocho mil seiscientos veintiséis temas distintos, un tono de menos cero coma setenta y seis, y united states como organización líder, con siete mil quinientas cincuenta y siete menciones. Las fórmulas completas están en el informe. El uno y el cuatro miden amplitud; el dos mide cambio en el tiempo; el tres y el seis miden qué se menciona más; y el cinco mide el sentimiento. Todos se calculan una vez por fecha, durante la tarea de agregación.

### Diapositiva 15: Resultado: volumen

**CAROLINE** · 13:44 - 14:41 (57 s)

> Pasemos a los resultados, empezando por el volumen, que sale de los conteos en MongoDB. El 23 de octubre hay setenta y nueve mil trescientos cuarenta y nueve registros. El sábado 24 baja a cuarenta y siete mil diecinueve y el domingo 25 a cuarenta mil doscientos veintiocho, es decir, cerca de un cuarenta y nueve por ciento menos que el 23. El lunes 26 se recupera a setenta y un mil ochocientos ochenta y tres y el 27 llega a ochenta y cuatro mil setecientos veintitrés. Es un patrón semanal esperable: se publican menos noticias el fin de semana. Este resultado también sirve como prueba de que la ingesta funciona: los conteos que vemos son los de los documentos realmente guardados en MongoDB, y coinciden con los del archivo de origen.

### Diapositiva 16: Resultado: tono

**MAYRA** · 14:41 - 15:26 (45 s)

> El segundo resultado es el tono promedio, que sale de Cassandra. Es negativo en las seis fechas, entre menos cero coma sesenta y seis y menos uno coma doce. El mínimo, menos uno coma doce, coincide con el domingo 25, justo el día de menor volumen. Una lectura posible es que con pocos registros cada noticia negativa pesa más en el promedio. Es una hipótesis que no probamos, pero el patrón es claro en los datos. Para quien lea el gráfico: el tono medio de GDELT va aproximadamente de menos diez a más diez, y todos nuestros días están en el rango ligeramente negativo.

### Diapositiva 17: Resultado: conciliación

**CAROLINE** · 15:26 - 16:11 (45 s)

> El tercer resultado es la conciliación. La última tarea del DAG compara, para cada fecha, los registros en MongoDB, Cassandra y Neo4j, y deben coincidir. La tabla muestra que coinciden en las seis fechas: la diferencia es cero, y suman cuatrocientos tres mil novecientos cuarenta y uno registros. Si alguna base no coincidiera, la tarea fallaría y el DAG no se marcaría como completo. Esta conciliación se ejecuta en cada corrida, no solo en esta verificación. En la práctica, esta tarea es la que nos permite afirmar que el pipeline funciona de extremo a extremo y no solo que cada pieza funciona por separado.

### Diapositiva 18: Dashboard: Panorama e Indicadores

**ALESSANDRO** · 16:11 - 16:53 (42 s)

> Ahora el dashboard. Lo hicimos en Streamlit y consulta las tres bases. La pestaña Panorama resume la fecha: cuatrocientos tres mil novecientos cuarenta y uno registros analizados, seis fechas cargadas, ochenta mil setecientos treinta y nueve registros el seis de noviembre y tres de tres bases conectadas. La pestaña Indicadores muestra los seis KPIs servidos desde Cassandra. Aquí vemos el top diez de temas: TAX_FNCACT lidera, presente en el ochenta y tres coma cuatro por ciento de los registros del día. Todo cambia al elegir otra fecha en el selector de arriba. Ahora lo mostramos en vivo.

**ALESSANDRO** · 16:53 - 17:53 (60 s)

> DEMOSTRACIÓN EN VIVO. Abrir el dashboard y cambiar la fecha del selector a 24/10/2026: el volumen baja a 47 019 y la variación a menos 40,7 por ciento. Volver a 06/11/2026. En Indicadores, bajar hasta el top diez de temas y señalar TAX_FNCACT. Decir: al cambiar la fecha, todo el tablero se recalcula desde Cassandra.

### Diapositiva 19: Dashboard: Documentos y Relaciones

**ALESSANDRO** · 17:53 - 18:22 (29 s)

> Las otras dos pestañas muestran las bases restantes. Documentos consulta MongoDB: permite filtrar por tema exacto o por organización y abrir un documento completo. Relaciones consulta Neo4j: muestra cuántos registros, relaciones con temas y relaciones con organizaciones hay, qué tan concentrada está la agenda y qué actores aparecen juntos. Con estas cuatro pestañas, el dashboard cumple el requisito de conectar las tres bases en una sola interfaz.

**CAROLINE** · 18:22 - 19:02 (40 s)

> DEMOSTRACIÓN EN VIVO, pestaña Documentos. Escribir una organización, por ejemplo reuters, y pulsar Consultar documentos. Decir: aquí MongoDB devuelve los registros tal como llegaron, con sus listas de temas y organizaciones. Abrir un registro en Documento completo y mostrar el JSON.

**FABRICIO** · 19:02 - 19:42 (40 s)

> DEMOSTRACIÓN EN VIVO, pestaña Relaciones. Mostrar las tarjetas de nodos y relaciones, bajar a Actores que aparecen juntos y señalar el par oval office y white house. Decir: esto lo responde Neo4j recorriendo aristas, sin joins.

### Diapositiva 20: Discusión

**MAYRA** · 19:42 - 20:09 (27 s)

> Como interpretación, cada base cubre una consulta propia que las otras no resuelven bien, y la conciliación confirma que el pipeline las mantiene consistentes. En términos de diseño, esto confirma que la persistencia políglota tiene sentido cuando los patrones de acceso son distintos. Su costo es operativo: hay tres sistemas que mantener, y por eso el orquestador y la conciliación son piezas centrales.

**FABRICIO** · 20:09 - 20:37 (28 s)

> También debemos declarar los límites. Solo cargamos seis fechas. Cassandra corre en un solo nodo con factor de replicación uno, y el grafo se limita a diez entidades por lista. Son decisiones del entorno local del curso, no de la arquitectura. Como trabajo futuro, nos interesa cargar más fechas, escalar Cassandra a varios nodos y agregar indicadores de grafo, como el grado de las organizaciones.

### Diapositiva 21: Conclusiones

**FABRICIO** · 20:37 - 20:44 (7 s)

> Concluimos. Primero, cada base resuelve un patrón de acceso distinto: documentos, KPIs por fecha y relaciones.

**ABEL** · 20:44 - 20:51 (7 s)

> Segundo, el DAG de Airflow automatiza las seis etapas, desde la descarga hasta los indicadores.

**ALESSANDRO** · 20:51 - 21:05 (14 s)

> Y tercero, las tres bases concilian: cuatrocientos tres mil novecientos cuarenta y uno registros con diferencia cero. El código y las evidencias están en el repositorio. Quedamos atentos a preguntas y comentarios.
