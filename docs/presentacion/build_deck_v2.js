const path = require('path');
const NM = path.join(process.env.TEMP, 'deck', 'node_modules');
const pptxgen = require(path.join(NM, 'pptxgenjs'));
const { applyTheme } = require('C:/Users/Yuri Abel/.claude/skills/synced/066deb66-16a6-42cb-abed-b837b7014eeb_9a04cfba-7d15-40d4-98df-d658754b9e85/pptx/scripts/apply_theme.js');
const OUT = process.argv[2];

// Estándar de presentación académica: fondo blanco, una sola tipografía, tres colores.
const THEME = {
  name: 'Global News Intelligence academico',
  headFontFace: 'Arial', bodyFontFace: 'Arial',
  colors: { dk1: '2D2D2D', lt1: 'FFFFFF', dk2: '1F4E79', lt2: 'F0F4F8',
    accent1: '2E75B6', accent2: '1F4E79', accent3: '777777', accent4: 'FFF2CC', accent5: 'CCCCCC', accent6: '2D2D2D',
    hlink: '2E75B6', folHlink: '777777' },
};
const K = { primary: '1F4E79', accent: '2E75B6', body: '2D2D2D', muted: '777777', rule: 'CCCCCC',
  hl: 'FFF2CC', hlLine: 'E6C800', hlText: '7A5200', white: 'FFFFFF', panel: 'F0F4F8', soft: 'A0BBDD', grey: '9AA5B1' };
const F = 'Arial';
const M = 0.5;

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.title = 'Global News Intelligence';
pres.author = 'Equipo Global News Intelligence';
pres.theme = { headFontFace: F, bodyFontFace: F };
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: 'PORTADA', background: { color: K.primary } });
pres.defineSlideMaster({
  title: 'CONTENIDO', background: { color: K.white },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: M, y: 0.4, w: 9.0, h: 0.85, fontFace: F, fontSize: 24, bold: true, color: C.text2, valign: 'top', align: 'left', margin: 0 }, text: '' } }],
  slideNumber: { x: 9.0, y: 5.25, w: 0.5, h: 0.25, fontFace: F, fontSize: 11, color: K.muted, align: 'right' },
});
pres.defineSlideMaster({
  title: 'CIERRE', background: { color: K.primary },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: M, y: 0.3, w: 9.0, h: 0.5, fontFace: F, fontSize: 22, color: 'A0BBDD', valign: 'top', align: 'left', margin: 0 }, text: '' } }],
});

const SECTIONS = ['Contexto', 'Datos', 'Diseño', 'Resultados', 'Cierre'];
function breadcrumb(s, current) {
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 10, h: 0.28, fill: { color: K.panel }, line: { color: K.panel }, objectName: 'Barra de sección' });
  const w = 10 / SECTIONS.length;
  SECTIONS.forEach((n, i) => {
    const on = n === current;
    s.addText(n, { x: i * w, y: 0, w, h: 0.28, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 11, bold: on, color: on ? K.accent : K.muted, objectName: 'Sección ' + n });
  });
}
function bullets(s, items, x, y, w, h, size = 20) {
  const runs = items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } }));
  s.addText(runs, { x, y, w, h, isTextBox: true, margin: 0, fontFace: F, fontSize: size, color: K.body, valign: 'top', paraSpaceAfter: 10, objectName: 'Puntos clave' });
}
function head(s, t, x, y, w) {
  s.addText(t, { x, y, w, h: 0.35, isTextBox: true, margin: 0, fontFace: F, fontSize: 20, bold: true, color: K.accent, objectName: 'Encabezado' });
}
function box(s, x, y, w, h, title, sub, fill, name) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.06, fill: { color: fill }, line: { color: fill }, objectName: name || title });
  s.addText(title, { x, y: y + 0.08, w, h: h * 0.5, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 16, bold: true, color: K.white });
  if (sub) s.addText(sub, { x: x + 0.05, y: y + h * 0.5, w: w - 0.1, h: h * 0.45, isTextBox: true, margin: 0, align: 'center', valign: 'top', fontFace: F, fontSize: 12, color: 'E6EEF8' });
}
function arrow(s, x1, y1, x2, y2) {
  s.addShape(pres.ShapeType.line, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1, line: { color: K.muted, width: 1.5, endArrowType: 'triangle' }, objectName: 'Flecha' });
}
function callout(s, text, x, y, w, h = 0.5) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.06, fill: { color: K.hl }, line: { color: K.hlLine, width: 1 }, objectName: 'Anotación' });
  s.addText(text, { x, y, w, h, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 14, bold: true, color: K.hlText, objectName: 'Texto de anotación' });
}
const TH = { bold: true, color: K.white, fill: { color: K.primary }, fontFace: F };
const TB = { solid: 1 };
const tblOpts = { border: { type: 'solid', color: K.rule, pt: 0.5 }, margin: [0.03, 0.1, 0.03, 0.1], valign: 'middle' };

const labels = ['23 oct', '24 oct', '25 oct', '26 oct', '27 oct', '6 nov'];
const chartBase = {
  catAxisLabelColor: K.muted, valAxisLabelColor: K.muted, catAxisLabelFontSize: 14, valAxisLabelFontSize: 14,
  catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', valGridLine: { color: 'E2E8F0', size: 0.5 }, catGridLine: { style: 'none' },
  showLegend: false, dataLabelFontFace: '+mn-lt', dataLabelColor: K.body, dataLabelFontSize: 14,
};

// ---------- Guion: segmentos por orador; la duración se calcula con 2,4 palabras por segundo ----------
const NM2 = path.join(process.env.TEMP, 'deck', 'node_modules');
const sharp = require(path.join(NM2, 'sharp'));
const CAP = 'z:/C26-2/BIGDATA/proy/proy2/karol/docs/evidencias_2026-11-16/capturas/recortes/';
const WPS = 2.3;
const NAMES = { A: 'ABEL', C: 'CAROLINE', M: 'MAYRA', F: 'FABRICIO', L: 'ALESSANDRO' };
const clock = { t: 0 };
const OWN = { A: 0, C: 0, M: 0, F: 0, L: 0 };
const VIDEO = { A: 1, C: 2, M: 3, F: 4, L: 5 };
let slideNo = 0;
const TOTALS = { A: 0, C: 0, M: 0, F: 0, L: 0 };
const GUION = [];
const mmss = (t) => `${Math.floor(t / 60)}:${String(Math.round(t % 60)).padStart(2, '0')}`;
function segs(num, titulo, list) {
  const lines = [];
  list.forEach(([who, text, fixed]) => {
    const secs = fixed || Math.max(5, Math.round(text.trim().split(/\s+/).length / WPS));
    const ini = clock.t, fin = clock.t + secs;
    const oi = OWN[who], of = OWN[who] + secs;
    clock.t = fin; OWN[who] = of; TOTALS[who] += secs;
    lines.push(`🎤 ${NAMES[who]} · VIDEO ${VIDEO[who]} DE 5 · ⏱ en su video ${mmss(oi)} - ${mmss(of)} · en el video final ${mmss(ini)} - ${mmss(fin)}\n“${text.trim()}”`);
    GUION.push({ num, titulo, who, ini, fin, secs, oi, of, text: text.trim() });
  });
  return lines.join('\n\n');
}
function content(title, section, cite, notes) {
  slideNo++;
  pres.addSection({ title: section + ': ' + title.slice(0, 30) });
  const s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: section + ': ' + title.slice(0, 30) });
  breadcrumb(s, section);
  s.addText(title, { placeholder: 'title' });
  if (cite) s.addText(cite, { x: M, y: 5.2, w: 8.3, h: 0.3, isTextBox: true, margin: 0, fontFace: F, fontSize: 12, color: K.muted, valign: 'middle', objectName: 'Cita' });
  s.addNotes(notes);
  return s;
}
const sizes = {};
async function loadSizes(names) { for (const n of names) { const m = await sharp(CAP + n + '.png').metadata(); sizes[n] = [m.width, m.height]; } }
function img(s, name, x, y, mw, mh, alt) {
  const [w, h] = sizes[name]; const k = Math.min(mw / w, mh / h);
  s.addImage({ path: CAP + name + '.png', x, y, w: w * k, h: h * k, altText: alt, objectName: 'Captura ' + name });
  return [w * k, h * k];
}

const SC = {
  'Portada': [['A', 'Hola, somos el equipo de Global News Intelligence. Presentaremos un pipeline que lleva noticias de GDELT a tres bases de datos y a un dashboard. Somos cinco. Yo soy Abel, a cargo de la arquitectura y de Airflow. Caroline presenta MongoDB, Mayra presenta Cassandra, Fabricio presenta Neo4j y Alessandro presenta los KPIs y el dashboard.']],
  'Motivación': [['A', 'Empecemos por el problema. GDELT publica cada día un archivo con cientos de miles de registros sobre noticias del mundo. En nuestra carga, del 23 de octubre al 6 de noviembre, llegaron entre cuarenta mil y ochenta y cinco mil registros por día, y sumamos cuatrocientos tres mil novecientos cuarenta y uno en seis fechas. Ese mismo dato se necesita para tres usos distintos. Primero, conservar el original sin perder nada. Segundo, responder indicadores diarios rápido. Y tercero, explorar qué temas y organizaciones aparecen juntos. Una sola base de datos no resuelve bien las tres cosas, y de ahí nace el proyecto.']],
  'Pregunta': [['A', 'Nuestra pregunta tiene dos partes. La primera es de modelado: qué base de datos conviene a cada tipo de dato de GDELT y por qué. La segunda es de ingeniería: si un flujo de Airflow puede automatizar todo el camino y dejar las tres bases conciliadas cada día. Nuestro aporte es un pipeline de extremo a extremo con seis KPIs y un dashboard que consulta las tres bases. Para responder, construimos primero el modelo de cada base y luego el flujo que las alimenta.']],
  'Arquitectura': [['A', 'Esta es la arquitectura. Todo parte de GDELT, que entrega los archivos diarios. Apache Airflow orquesta el flujo con un DAG de ocho tareas. Primero los datos llegan a MongoDB, que es nuestra fuente de verdad. Desde MongoDB se alimentan en paralelo Cassandra, que guarda los KPIs por fecha, y Neo4j, que guarda las relaciones. Finalmente, el dashboard de Streamlit consulta las tres bases. Todo corre en contenedores con Docker Compose: MongoDB 8, Cassandra 5, Neo4j 5.26 y Airflow 2.11. Quiero resaltar dos decisiones. MongoDB va primero, así que cualquier fallo posterior se repara volviendo a leer los documentos originales. Y Cassandra y Neo4j leen desde MongoDB, lo que garantiza que las tres bases parten del mismo conjunto de registros.']],
  'Justificación': [['A', 'Esta tabla resume la justificación técnica de dónde vive cada dato. El registro completo, con listas anidadas, va a MongoDB, porque un documento lo guarda tal como llega. Los KPIs diarios y los rankings van a Cassandra, porque se leen siempre por fecha y su modelo da lecturas rápidas y versiones de cada publicación. Y las relaciones entre registros, temas y organizaciones van a Neo4j, porque recorrer aristas es nativo y evita joins costosos. Si usáramos una sola base, perderíamos alguna de estas tres consultas. Mis compañeros lo detallan al presentar cada base.']],
  'DAG de Airflow': [['A', 'El DAG de Airflow tiene ocho tareas y cubre las seis etapas exigidas. Primero select_partition fija la fecha. Luego extract descarga el archivo, validate comprueba su calidad y transform lo convierte a JSON por líneas. Después load_mongodb carga los documentos. A partir de ahí, aggregate_cassandra y load_neo4j corren en paralelo, y la última tarea, generate_indicators, concilia las tres bases y publica el reporte. Se ejecuta cada día a las seis de la mañana con una expresión cron, con dos reintentos de cinco minutos y sin catchup. Ya verificamos una ejecución programada real: la del seis de noviembre, con ochenta mil setecientos treinta y nueve registros conciliados. Cada tarea registra su estado en MongoDB, y como las cargas son idempotentes, volver a ejecutar una fecha no genera duplicados. Con esto el flujo queda automatizado. Le paso la palabra a Caroline, que empieza con los datos y MongoDB.']],
  'Datos': [['C', 'Gracias, Abel. Soy Caroline y empiezo por los datos. Son el Global Knowledge Graph de GDELT: un archivo CSV tabulado dentro de un ZIP por cada día. Cada registro tiene once columnas, y tres son las que más usamos: THEMES, con la lista de temas; ORGANIZATIONS, con las organizaciones mencionadas; y TONE, con el tono del registro. Antes de cargar validamos el esquema exacto de las once columnas, que la fecha tenga formato válido y que el tono sea numérico. En la muestra de ochenta y tres mil registros no hubo ninguno mal formado. También vimos que algunos campos vienen vacíos con frecuencia, como las personas o los eventos asociados, por lo que el modelo tiene que tolerar campos faltantes sin fallar. Y como cada archivo trae los registros de su día, el volumen cambia mucho de una fecha a otra, algo que veremos en los resultados.']],
  'MongoDB: modelo': [['C', 'Por qué MongoDB: el registro llega con listas de temas y organizaciones de longitud variable, y un documento las guarda tal como llegan, sin normalizarlas en varias tablas. El modelo tiene tres colecciones. gkg_records guarda un documento por registro, con las listas ya separadas. ingestion_history guarda un documento por archivo cargado, con su estado y sus conteos. Y pipeline_history guarda el estado de cada etapa del DAG, incluido el tipo de error si algo falla. La carga usa upsert por el identificador, con setOnInsert, así que repetir una fecha no duplica documentos: es idempotente. Además tenemos un validador JSON Schema, e índices por fecha, por archivo de origen y sobre la lista de temas, para que el dashboard filtre rápido por un tema exacto sin recorrer toda la colección.']],
  'MongoDB: ingesta y CRUD': [['C', 'El script de ingesta lee el archivo transformado y carga los documentos por lotes. Al terminar, el pipeline comprueba que el conteo en MongoDB sea igual al conteo validado: para el seis de noviembre, ochenta mil setecientos treinta y nueve. En la captura vemos el explorador documental del dashboard, donde cada fila conserva el identificador, la cantidad de artículos asociados y las listas de temas y organizaciones tal como llegaron. También verificamos el CRUD completo: crear, leer, actualizar y borrar, eliminando los datos de prueba al final. Un detalle del modelo: el identificador de cada documento se deriva del archivo y de la fila, por eso volver a cargar la misma fecha reemplaza en lugar de duplicar. El historial de ingesta guarda cuántos registros se procesaron y cuándo terminó cada carga, lo que nos permite auditarlas. Y la etapa solo se da por completada si el conteo coincide con el del archivo validado.'],
    ['C', 'DEMOSTRACIÓN EN PANTALLA, pestaña Documentos del dashboard. Escribir una organización, por ejemplo reuters, y pulsar Consultar documentos. Decir: aquí MongoDB devuelve los registros tal como llegaron. Abrir un registro en Documento completo y mostrar el JSON. Cerrar diciendo: le paso la palabra a Mayra, que presenta Cassandra.', 55]],
  'Cassandra: modelo': [['M', 'Gracias, Caroline. Soy Mayra y les presento Cassandra. Por qué Cassandra: los KPIs se leen siempre por fecha y se escriben una vez al día, y Cassandra está pensada para eso, con lecturas rápidas por partición. Por eso modelamos una tabla por consulta. daily_news_metrics guarda una fila por fecha con volumen, variación, diversidad y tono. Las tablas de temas y de organizaciones guardan los diez primeros de cada fecha. Para no mostrar nunca datos a medias, cada publicación escribe una versión nueva identificada con un UUID de generación: primero se escribe la versión, luego se verifican los conteos y solo al final se activa la generación. Usamos consistencia LOCAL_QUORUM, en un nodo con factor de replicación uno, suficiente para el entorno local del curso.']],
  'Cassandra: ingesta y recuperación': [['M', 'El script de agregación calcula los KPIs desde MongoDB y los publica en Cassandra con ese protocolo de versiones. Gracias a las versiones, si una publicación falla a medias, el dashboard sigue leyendo la última generación completa y nunca ve números parciales. La captura muestra las tarjetas del dashboard servidas desde Cassandra: volumen, variación, diversidad temática y tono promedio del seis de noviembre. Además verificamos la recuperación: reiniciamos Cassandra y los KPIs publicados siguieron disponibles. El CRUD también quedó probado, con limpieza de los datos de prueba.'],
    ['M', 'DEMOSTRACIÓN EN PANTALLA, pestaña Indicadores. Cambiar la fecha del selector a 24/10/2026: el volumen baja a 47 019 y la variación a menos 40,7 por ciento. Volver a 06/11/2026. Decir: al cambiar la fecha, todo se recalcula leyendo Cassandra por partición de fecha.', 45]],
  'Resultado: volumen': [['M', 'Con los KPIs publicados, veamos los resultados. El primero es el volumen, el KPI uno, servido desde Cassandra. El 23 de octubre hay setenta y nueve mil trescientos cuarenta y nueve registros. El sábado 24 baja a cuarenta y siete mil diecinueve y el domingo 25 a cuarenta mil doscientos veintiocho, es decir, cerca de un cuarenta y nueve por ciento menos que el 23. El lunes 26 se recupera a setenta y un mil ochocientos ochenta y tres y el 27 llega a ochenta y cuatro mil setecientos veintitrés. Es un patrón semanal esperable: se publican menos noticias el fin de semana. Estos conteos coinciden con los de los documentos guardados en MongoDB.']],
  'Resultado: tono': [['M', 'El segundo resultado es el tono promedio. Es negativo en las seis fechas, entre menos cero coma sesenta y seis y menos uno coma doce. El mínimo, menos uno coma doce, coincide con el domingo 25, justo el día de menor volumen. Una lectura posible es que con pocos registros cada noticia negativa pesa más en el promedio. Es una hipótesis que no probamos, pero el patrón es claro. Recuerden que el tono de GDELT va aproximadamente de menos diez a más diez, así que todos nuestros días están en el rango ligeramente negativo. Esto también ilustra por qué la variación se calcula frente a la fecha anterior disponible y no frente al día calendario previo: el seis de noviembre se compara con el veintisiete de octubre. Le paso la palabra a Fabricio, que presenta Neo4j.']],
  'Neo4j: modelo': [['F', 'Gracias, Mayra. Soy Fabricio y les presento Neo4j. Por qué Neo4j: la pregunta de qué temas y organizaciones aparecen juntos es una pregunta de relaciones, y en un grafo las relaciones son datos de primera clase. El modelo tiene tres tipos de nodos: GKGRecord, para cada registro; Theme, para cada tema; y Organization, para cada organización. Y dos relaciones: HAS_THEME, del registro a sus temas, y MENTIONS_ORG, del registro a las organizaciones que menciona. Para saber qué temas aparecen junto a una organización basta recorrer dos saltos desde el nodo, algo que en un modelo relacional exigiría varios joins sobre tablas grandes. Creamos restricciones de unicidad, y para controlar el tamaño enlazamos las diez primeras entidades de cada lista. Entre las seis fechas suman unos tres coma cuatro millones de aristas de temas y uno coma uno de organizaciones, sobre cuatrocientos tres mil nodos de registro.']],
  'Neo4j: ingesta y CRUD': [['F', 'El script carga el grafo con MERGE en lotes de cien, de modo que repetir una fecha no duplica nodos ni relaciones. Gracias a eso podemos hacer preguntas de red. La captura es del dashboard: los pares de organizaciones que más coinciden en los registros. El par más frecuente es oval office y white house, con ochocientos cinco registros en común. En Neo4j también probamos el CRUD, incluyendo crear y borrar una relación. Antes de cargar, el script asegura las restricciones de unicidad y luego procesa los registros del día leyéndolos desde MongoDB. Como usa MERGE, es seguro reejecutarlo, y el pipeline lo invoca justamente para reparar nodos ausentes sin duplicar los existentes.'],
    ['F', 'DEMOSTRACIÓN EN PANTALLA, pestaña Relaciones. Mostrar las tarjetas de registros y relaciones, bajar a Actores que aparecen juntos y señalar el par oval office y white house. Decir: esto lo responde Neo4j recorriendo aristas, sin joins.', 40]],
  'Neo4j: resultado': [['F', 'El grafo también nos permite medir qué tan concentrada está la agenda. El seis de noviembre hay sesenta y seis mil trescientas veinte entidades únicas. Las diez organizaciones más citadas acumulan solo el once por ciento de las menciones, y el setenta por ciento de las organizaciones se menciona una sola vez: es una agenda fragmentada, con una cola larga de actores. Además, cada registro enlaza en promedio once coma tres temas y organizaciones, lo que da contexto a cada noticia. Por eso el dashboard permite explorar las conexiones de las veinticinco entidades más mencionadas.']],
  'Resultado: conciliación': [['F', 'Para cerrar las bases, la conciliación. La última tarea del DAG compara, para cada fecha, los registros en MongoDB, Cassandra y Neo4j, y deben coincidir. La tabla muestra que coinciden en las seis fechas: la diferencia es cero, y suman cuatrocientos tres mil novecientos cuarenta y uno registros. Si alguna base no coincidiera, la tarea fallaría y el DAG no se marcaría como completo. Esto nos permite afirmar que el pipeline funciona de extremo a extremo y no solo cada pieza por separado. Cada corrida deja ese reporte en un archivo de indicadores y el estado de cada etapa en el historial del pipeline. Le paso la palabra a Alessandro, con los KPIs y el dashboard.']],
  'KPIs': [['L', 'Gracias, Fabricio. Soy Alessandro y presento los KPIs y el dashboard. Implementamos seis KPIs, y el mínimo pedido era cinco. El uno es el volumen diario. El dos es la variación diaria frente a la fecha disponible anterior. El tres es la frecuencia de temas, con los diez más frecuentes. El cuatro es la diversidad temática, cuántos códigos distintos aparecen. El cinco es el tono promedio. Y el seis son las organizaciones más mencionadas. Los valores del seis de noviembre son: ochenta mil setecientos treinta y nueve registros, una variación de menos cuatro coma siete por ciento, un tema líder con sesenta y siete mil trescientos cuarenta y siete registros, ocho mil seiscientos veintiséis temas distintos, un tono de menos cero coma setenta y seis, y united states como organización líder, con siete mil quinientas cincuenta y siete menciones. Todos se calculan una vez por fecha, durante la tarea de agregación, y las fórmulas completas están en el informe.']],
  'Dashboard: Panorama e Indicadores': [['L', 'El dashboard lo hicimos en Streamlit y consulta las tres bases, con cuatro pestañas. Panorama resume la fecha: cuatrocientos tres mil novecientos cuarenta y uno registros analizados, seis fechas cargadas, ochenta mil setecientos treinta y nueve registros el seis de noviembre y tres de tres bases conectadas. Indicadores muestra los seis KPIs servidos desde Cassandra; aquí vemos el top diez de temas, con TAX_FNCACT presente en el ochenta y tres coma cuatro por ciento de los registros. Documentos consulta MongoDB y Relaciones consulta Neo4j, como mostraron Caroline y Fabricio. Con las cuatro pestañas el dashboard cumple el requisito de conectar las tres bases en una sola interfaz.'],
    ['L', 'DEMOSTRACIÓN EN PANTALLA, pestaña Panorama. Mostrar las cifras y el diagrama de las ocho tareas, cambiar la fecha del selector y señalar que las cuatro pestañas se actualizan. Decir: ninguna pestaña calcula nada por su cuenta, todo viene de las bases.', 45]],
  'Discusión': [['L', 'Como interpretación, cada base cubre una consulta propia que las otras no resuelven bien, y la conciliación confirma que el pipeline las mantiene consistentes. La persistencia políglota tiene sentido cuando los patrones de acceso son distintos, y su costo es operativo: hay tres sistemas que mantener, por eso el orquestador y la conciliación son piezas centrales. También debemos declarar los límites. Solo cargamos seis fechas, Cassandra corre en un solo nodo con factor de replicación uno, y el grafo se limita a diez entidades por lista. Son decisiones del entorno local del curso, no de la arquitectura. Como trabajo futuro, nos interesa cargar más fechas, escalar Cassandra a varios nodos y agregar indicadores de grafo.']],
  'Conclusiones': [['L', 'Para concluir. Uno, MongoDB conserva el registro original y su carga es idempotente. Dos, Cassandra sirve KPIs versionados y recuperables. Tres, Neo4j responde preguntas de relaciones sin joins. Cuatro, el DAG de Airflow automatiza las seis etapas y las tres bases concilian: cuatrocientos tres mil novecientos cuarenta y uno registros con diferencia cero. Y cinco, seis KPIs y un dashboard unen las tres bases. El código y las evidencias están en el repositorio. Quedamos atentos a preguntas y comentarios.']],
};

(async () => {
  await loadSizes(['panorama_resumen', 'panorama_flujo', 'indicadores_kpis', 'indicadores_temas', 'documentos_explorador', 'relaciones_resumen', 'relaciones_coocurrencia']);

  // ===== 1. Portada =====
  pres.addSection({ title: 'Portada' });
  let s = pres.addSlide({ masterName: 'PORTADA', sectionTitle: 'Portada' });
  s.addText('Tres bases de datos con roles distintos mantienen conciliadas 403 941 noticias de GDELT', { x: 0.7, y: 1.1, w: 8.6, h: 1.8, isTextBox: true, margin: 0, fontFace: F, fontSize: 32, bold: true, color: K.white, valign: 'top', align: 'left' });
  s.addText('Global News Intelligence: pipeline automatizado con MongoDB, Cassandra y Neo4j', { x: 0.7, y: 3.05, w: 8.6, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 16, color: K.soft });
  s.addText('Abel  ·  Alessandro  ·  Caroline  ·  Fabricio  ·  Mayra', { x: 0.7, y: 3.65, w: 8.6, h: 0.35, isTextBox: true, margin: 0, fontFace: F, fontSize: 16, bold: true, color: K.white });
  s.addText('Universidad de Ingeniería y Tecnología (UTEC)  ·  Proyecto 2, curso de Big Data', { x: 0.7, y: 4.05, w: 8.6, h: 0.35, isTextBox: true, margin: 0, fontFace: F, fontSize: 14, color: 'CADCFC' });
  s.addText('Noviembre de 2026', { x: 0.7, y: 4.4, w: 8.6, h: 0.35, isTextBox: true, margin: 0, fontFace: F, fontSize: 14, color: 'CADCFC' });
  slideNo++;
  s.addNotes(segs(slideNo + 0, 'Portada', SC['Portada']));

  // ===== 2. Motivación =====
  s = content('GDELT publica cientos de miles de registros por día y una sola base no responde todas las consultas', 'Contexto',
    'GDELT Project; Leetaru y Schrodt (2013)',
    segs(slideNo + 1, 'Motivación', SC['Motivación']));
  bullets(s, ['Cada día llegan 40 000 a 85 000 registros', 'Hay que conservar el original', 'Los indicadores deben responder rápido', 'Las relaciones piden recorrer un grafo'], M, 1.5, 5.2, 3.4);
  s.addShape(pres.ShapeType.roundRect, { x: 6.2, y: 1.5, w: 3.3, h: 3.2, rectRadius: 0.06, fill: { color: K.panel }, line: { color: K.rule, width: 0.75 }, objectName: 'Panel de cifra' });
  s.addText('403 941', { x: 6.2, y: 1.9, w: 3.3, h: 0.9, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 44, bold: true, color: K.primary });
  s.addText('registros GKG en seis fechas, del 23 de octubre al 6 de noviembre de 2026', { x: 6.45, y: 2.9, w: 2.8, h: 1.2, isTextBox: true, margin: 0, align: 'center', valign: 'top', fontFace: F, fontSize: 16, color: K.body });

  // ===== 3. Pregunta =====
  s = content('Este proyecto pregunta qué base de datos conviene a cada tipo de dato y si el flujo puede automatizarse', 'Contexto', null,
    segs(slideNo + 1, 'Pregunta', SC['Pregunta']));
  s.addShape(pres.ShapeType.roundRect, { x: 1.0, y: 1.6, w: 8.0, h: 1.7, rectRadius: 0.1, fill: { color: 'EBF3FA' }, line: { color: K.accent, width: 1.5 }, objectName: 'Pregunta' });
  s.addText('¿Qué base resuelve mejor documentos, indicadores y relaciones de GDELT, y puede un DAG de Airflow mantenerlas conciliadas cada día?', { x: 1.25, y: 1.7, w: 7.5, h: 1.5, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 22, color: K.primary });
  s.addText([{ text: 'Aporte: ', options: { bold: true } }, { text: 'pipeline de extremo a extremo con seis KPIs y un dashboard que consulta las tres bases.' }],
    { x: M, y: 3.7, w: 9.0, h: 1.0, isTextBox: true, margin: 0, fontFace: F, fontSize: 20, color: K.body, valign: 'top' });

  // ===== 5. Arquitectura =====
  s = content('Airflow orquesta un flujo único que va de GDELT a tres bases y termina en un dashboard', 'Diseño',
    'Docker Compose: MongoDB 8.0, Cassandra 5.0, Neo4j 5.26, Airflow 2.11, Streamlit 1.66',
    segs(slideNo + 1, 'Arquitectura', SC['Arquitectura']));
  box(s, M, 2.45, 1.5, 1.0, 'GDELT', 'Archivos GKG', K.muted);
  box(s, 2.3, 2.45, 1.5, 1.0, 'Airflow', 'DAG de 8 tareas', K.primary);
  box(s, 4.1, 2.45, 1.6, 1.0, 'MongoDB', 'Documentos', K.accent);
  box(s, 6.1, 1.45, 1.6, 1.0, 'Cassandra', 'KPIs por fecha', K.accent);
  box(s, 6.1, 3.45, 1.6, 1.0, 'Neo4j', 'Relaciones', K.accent);
  box(s, 8.1, 2.45, 1.4, 1.0, 'Streamlit', 'Dashboard', K.primary);
  arrow(s, 2.0, 2.95, 2.3, 2.95); arrow(s, 3.8, 2.95, 4.1, 2.95);
  arrow(s, 5.7, 2.7, 6.1, 1.95); arrow(s, 5.7, 3.2, 6.1, 3.95);
  arrow(s, 7.7, 1.95, 8.1, 2.7); arrow(s, 7.7, 3.95, 8.1, 3.2);
  s.addText('Cada base recibe los datos que su modelo consulta mejor', { x: M, y: 4.75, w: 9.0, h: 0.35, isTextBox: true, margin: 0, fontFace: F, fontSize: 16, color: K.body });

  // ===== 6. Justificación =====
  s = content('Cada tipo de dato vive en la base cuyo modelo responde mejor a su patrón de consulta', 'Diseño',
    'Criterio de diseño del proyecto; documentación de MongoDB, Cassandra y Neo4j',
    segs(slideNo + 1, 'Justificación', SC['Justificación']));
  const jr = [[{ text: 'Dato', options: { ...TH, fontSize: 16 } }, { text: 'Base', options: { ...TH, fontSize: 16 } }, { text: 'Motivo', options: { ...TH, fontSize: 16 } }]];
  [['Registro GKG completo', 'MongoDB', 'Esquema flexible y upsert idempotente'], ['KPIs diarios y rankings', 'Cassandra', 'Lectura por fecha y versiones'], ['Temas y organizaciones por registro', 'Neo4j', 'Recorrido de aristas sin joins']]
    .forEach(([a, b, c], i) => { const f = { fill: { color: i % 2 ? K.panel : K.white } }; jr.push([{ text: a, options: { fontFace: F, fontSize: 18, color: K.body, ...f } }, { text: b, options: { fontFace: F, fontSize: 18, bold: true, color: K.primary, ...f } }, { text: c, options: { fontFace: F, fontSize: 18, color: K.body, ...f } }]); });
  s.addTable(jr, { x: M, y: 1.6, w: 9.0, colW: [3.4, 1.7, 3.9], rowH: [0.45, 0.8, 0.8, 0.8], ...tblOpts, objectName: 'Tabla de justificación' });

  // ===== 7. DAG =====
  s = content('Un DAG de ocho tareas cubre las seis etapas exigidas y se ejecuta cada día a las 06:00', 'Diseño',
    'Apache Airflow 2.11.1, API TaskFlow (Apache Software Foundation, 2026)',
    segs(slideNo + 1, 'DAG de Airflow', SC['DAG de Airflow']));
  const tk = [['select_partition', K.muted], ['extract', K.muted], ['validate', K.primary], ['transform', K.primary], ['load_mongodb', K.accent]];
  tk.forEach(([t, c], i) => {
    const x = M + i * 1.8;
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.55, w: 1.55, h: 0.6, rectRadius: 0.06, fill: { color: c }, line: { color: c }, objectName: 'Tarea ' + t });
    s.addText(t, { x, y: 1.55, w: 1.55, h: 0.6, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 12, bold: true, color: K.white });
    if (i < 4) arrow(s, x + 1.55, 1.85, x + 1.8, 1.85);
  });
  [['aggregate_cassandra', 2.75], ['load_neo4j', 3.55]].forEach(([t, y]) => {
    s.addShape(pres.ShapeType.roundRect, { x: 5.8, y, w: 2.1, h: 0.6, rectRadius: 0.06, fill: { color: K.accent }, line: { color: K.accent }, objectName: 'Tarea ' + t });
    s.addText(t, { x: 5.8, y, w: 2.1, h: 0.6, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 12, bold: true, color: K.white });
  });
  const ln = (x, y, w, h, arr) => s.addShape(pres.ShapeType.line, { x, y, w, h, line: { color: K.muted, width: 1.5, ...(arr ? { endArrowType: 'triangle' } : {}) }, objectName: 'Conector' });
  ln(8.475, 2.15, 0, 0.3); ln(5.55, 2.45, 2.925, 0); ln(5.55, 2.45, 0, 1.4);
  ln(5.55, 3.05, 0.25, 0, true); ln(5.55, 3.85, 0.25, 0, true);
  ln(7.9, 3.05, 0.25, 0); ln(7.9, 3.85, 0.25, 0); ln(8.15, 3.05, 0, 0.8); ln(8.15, 3.45, 0.15, 0, true);
  s.addShape(pres.ShapeType.roundRect, { x: 8.3, y: 3.05, w: 1.2, h: 0.8, rectRadius: 0.06, fill: { color: K.primary }, line: { color: K.primary }, objectName: 'Tarea generate_indicators' });
  s.addText('generate_\nindicators', { x: 8.3, y: 3.05, w: 1.2, h: 0.8, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 11, bold: true, color: K.white });
  bullets(s, ['Cron diario 0 6 * * *', '2 reintentos, 5 minutos', 'Sin catchup'], M, 2.75, 4.8, 1.8, 18);

  // ===== 4. Datos =====
  s = content('El GKG diario aporta 11 columnas por registro y temas, organizaciones y tono concentran la señal', 'Datos',
    'Fuente: GDELT GKG diario, formato CSV tabulado dentro de ZIP (Leetaru y Schrodt, 2013)',
    segs(slideNo + 1, 'Datos', SC['Datos']));
  const dr = [[{ text: 'Campo', options: { ...TH, fontSize: 16 } }, { text: 'Contenido', options: { ...TH, fontSize: 16 } }]];
  [['DATE', 'Fecha de publicación', false], ['THEMES', 'Lista de temas', true], ['ORGANIZATIONS', 'Lista de organizaciones', true], ['TONE', 'Tono del registro', true], ['Otros 7 campos', 'Personas, ubicaciones, URL', false]]
    .forEach(([a, b, key], i) => { const f = { fill: { color: key ? 'DCEBF8' : (i % 2 ? K.panel : K.white) } }; dr.push([{ text: a, options: { fontFace: F, fontSize: 16, bold: key, color: K.body, ...f } }, { text: b, options: { fontFace: F, fontSize: 16, color: K.body, ...f } }]); });
  s.addTable(dr, { x: M, y: 1.5, w: 5.6, colW: [2.2, 3.4], rowH: 0.5, ...tblOpts, objectName: 'Tabla de campos' });
  s.addText('Los tres campos resaltados alimentan los KPIs y el grafo', { x: M, y: 4.6, w: 5.6, h: 0.35, isTextBox: true, margin: 0, fontFace: F, fontSize: 14, color: K.muted });
  head(s, 'Controles', 6.5, 1.5, 3.0);
  bullets(s, ['Esquema de 11 columnas', 'Fecha válida', 'Tono numérico', 'Muestra: 0 registros mal formados'], 6.5, 1.95, 3.0, 2.9, 18);

  // ===== 8. MongoDB modelo =====
  s = content('MongoDB conserva el registro original y hace idempotente la carga de cada fecha', 'Diseño',
    'MongoDB, Inc. (2026), manual de MongoDB',
    segs(slideNo + 1, 'MongoDB: modelo', SC['MongoDB: modelo']));
  [['gkg_records', 'Un documento por registro'], ['ingestion_history', 'Un documento por archivo'], ['pipeline_history', 'Estado por etapa del DAG']].forEach(([n, d], i) => {
    const y = 1.5 + i * 1.15;
    s.addShape(pres.ShapeType.roundRect, { x: M, y, w: 4.8, h: 1.0, rectRadius: 0.06, fill: { color: K.panel }, line: { color: K.accent, width: 1.25 }, objectName: 'Colección ' + n });
    s.addText(n, { x: M + 0.2, y: y + 0.1, w: 4.4, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 18, bold: true, color: K.primary, valign: 'middle' });
    s.addText(d, { x: M + 0.2, y: y + 0.5, w: 4.4, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 16, color: K.body, valign: 'middle' });
  });
  bullets(s, ['Upsert por _id: repetir una fecha no duplica', 'Validador JSON Schema', 'Índices por fecha y archivo'], 5.6, 1.5, 3.9, 3.3);

  // ===== 9. MongoDB ingesta =====
  s = content('La ingesta carga por lotes con upsert y el conteo en MongoDB coincide con el archivo validado', 'Diseño',
    'Captura: explorador documental del dashboard, fecha 06/11/2026 (docs/evidencias_2026-11-16/capturas)',
    segs(slideNo + 1, 'MongoDB: ingesta y CRUD', SC['MongoDB: ingesta y CRUD']));
  img(s, 'documentos_explorador', M, 1.4, 5.3, 3.7, 'Explorador documental del dashboard con 80 739 registros de MongoDB');
  bullets(s, ['Carga por lotes con upsert', 'Conteo validado: 80 739', 'CRUD: crear, leer, actualizar y borrar'], 6.1, 1.5, 3.4, 3.3, 18);

  // ===== 10. Cassandra modelo =====
  s = content('Cassandra publica cada KPI como una versión inmutable que se consulta por fecha', 'Diseño',
    'Apache Software Foundation (2026), documentación de Apache Cassandra',
    segs(slideNo + 1, 'Cassandra: modelo', SC['Cassandra: modelo']));
  [['1', 'Escribir versión nueva'], ['2', 'Verificar conteos'], ['3', 'Activar la generación']].forEach(([n, t], i) => {
    const y = 1.5 + i * 1.15;
    s.addShape(pres.ShapeType.roundRect, { x: M, y, w: 4.8, h: 0.9, rectRadius: 0.06, fill: { color: i === 2 ? K.primary : K.accent }, line: { color: K.accent }, objectName: 'Paso ' + n });
    s.addText(n + '. ' + t, { x: M + 0.2, y, w: 4.4, h: 0.9, isTextBox: true, margin: 0, fontFace: F, fontSize: 18, bold: true, color: K.white, valign: 'middle' });
    if (i < 2) arrow(s, M + 2.4, y + 0.9, M + 2.4, y + 1.15);
  });
  bullets(s, ['Una tabla por consulta de KPI', 'Lectura por partición de fecha', 'Consistencia LOCAL_QUORUM'], 5.6, 1.5, 3.9, 3.3);

  // ===== 11. Cassandra ingesta =====
  s = content('El script publica los KPIs desde MongoDB y la recuperación tras reiniciar está verificada', 'Diseño',
    'Captura: pestaña Indicadores del dashboard, fecha 06/11/2026 (docs/evidencias_2026-11-16/capturas)',
    segs(slideNo + 1, 'Cassandra: ingesta y recuperación', SC['Cassandra: ingesta y recuperación']));
  img(s, 'indicadores_kpis', M, 1.4, 5.3, 3.7, 'Tarjetas de KPI servidas desde Cassandra y gráficos de cobertura');
  bullets(s, ['Versión nueva con UUID', 'Se activa tras verificar', 'Recuperación tras reinicio verificada'], 6.1, 1.5, 3.4, 3.3, 18);

  // ===== 15. Volumen =====
  s = content('El volumen cae 49 % durante el fin de semana del 24 y 25 de octubre y se recupera el lunes', 'Resultados',
    'Fuente: KPI 1, volumen diario por fecha, publicado en Cassandra (coincide con MongoDB)',
    segs(slideNo + 1, 'Resultado: volumen', SC['Resultado: volumen']));
  s.addChart(pres.charts.BAR, [{ name: 'Registros', labels, values: [79349, 47019, 40228, 71883, 84723, 80739] }], {
    x: M, y: 1.4, w: 5.4, h: 3.7, barDir: 'col', chartColors: [K.grey, K.accent, K.primary, K.grey, K.grey, K.grey],
    showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '#,##0', dataLabelFontSize: 12, valAxisMaxVal: 100000, valAxisLabelFormatCode: '#,##0', ...chartBase,
    showValAxisTitle: true, valAxisTitle: 'Registros', valAxisTitleColor: K.muted, valAxisTitleFontSize: 14, objectName: 'Gráfico de volumen',
  });
  callout(s, '−49 %\nfrente al 23 oct', 2.55, 1.45, 1.45, 0.65);
  bullets(s, ['Sábado 24: 47 019', 'Domingo 25: 40 228', 'Lunes 26: 71 883'], 6.2, 1.5, 3.3, 3.3, 18);

  // ===== 16. Tono =====
  s = content('El tono promedio es negativo en todas las fechas y toca su mínimo cuando el volumen es menor', 'Resultados',
    'Fuente: KPI 5, tono promedio por fecha, publicado en Cassandra',
    segs(slideNo + 1, 'Resultado: tono', SC['Resultado: tono']));
  s.addChart(pres.charts.LINE, [{ name: 'Tono promedio', labels, values: [-0.83, -1.06, -1.12, -0.67, -0.66, -0.76] }], {
    x: M, y: 1.4, w: 5.4, h: 3.7, chartColors: [K.accent], lineSize: 3, lineDataSymbolSize: 9,
    showValue: true, dataLabelPosition: 't', dataLabelFormatCode: '0.00', dataLabelFontSize: 12, valAxisMinVal: -1.4, valAxisMaxVal: -0.4, valAxisLabelFormatCode: '0.0', ...chartBase,
    showValAxisTitle: true, valAxisTitle: 'Tono promedio', valAxisTitleColor: K.muted, valAxisTitleFontSize: 14, objectName: 'Gráfico de tono',
  });
  callout(s, 'Mínimo: −1,12 (25 oct)', 3.0, 3.85, 2.3, 0.45);
  bullets(s, ['Rango: −1,12 a −0,66', 'Mínimo el 25 oct', 'Mayor volumen, tono menos negativo'], 6.2, 1.5, 3.3, 3.3, 18);

  // ===== 12. Neo4j modelo =====
  s = content('Neo4j conecta registros, temas y organizaciones con unos 4,5 millones de aristas', 'Diseño',
    'Neo4j, Inc. (2026), manual de Cypher',
    segs(slideNo + 1, 'Neo4j: modelo', SC['Neo4j: modelo']));
  [['Theme', 0.5, K.accent], ['GKGRecord', 2.55, K.primary], ['Organization', 4.6, K.accent]].forEach(([t, x, c]) => {
    s.addShape(pres.ShapeType.ellipse, { x, y: 2.3, w: 1.4, h: 1.1, fill: { color: c }, line: { color: c }, objectName: 'Nodo ' + t });
    s.addText(t, { x, y: 2.3, w: 1.4, h: 1.1, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 14, bold: true, color: K.white });
  });
  arrow(s, 2.55, 2.85, 1.9, 2.85); arrow(s, 3.95, 2.85, 4.6, 2.85);
  s.addText('HAS_THEME', { x: 1.0, y: 3.5, w: 1.6, h: 0.3, isTextBox: true, margin: 0, align: 'center', fontFace: F, fontSize: 12, color: K.muted });
  s.addText('MENTIONS_ORG', { x: 3.5, y: 3.5, w: 1.8, h: 0.3, isTextBox: true, margin: 0, align: 'center', fontFace: F, fontSize: 12, color: K.muted });
  s.addText('Esquema del grafo', { x: M, y: 4.2, w: 5.1, h: 0.3, isTextBox: true, margin: 0, fontFace: F, fontSize: 14, color: K.muted });
  bullets(s, ['3,4 M de aristas HAS_THEME', '1,1 M de aristas MENTIONS_ORG', 'Diez entidades por lista'], 6.2, 1.5, 3.3, 3.3, 18);

  // ===== 13. Neo4j ingesta =====
  s = content('La ingesta usa MERGE en lotes de 100 y permite preguntar qué organizaciones aparecen juntas', 'Diseño',
    'Captura: pestaña Relaciones del dashboard, fecha 06/11/2026 (docs/evidencias_2026-11-16/capturas)',
    segs(slideNo + 1, 'Neo4j: ingesta y CRUD', SC['Neo4j: ingesta y CRUD']));
  img(s, 'relaciones_coocurrencia', M, 1.4, 5.3, 3.7, 'Pares de organizaciones que más coinciden en los registros, según Neo4j');
  bullets(s, ['MERGE en lotes de 100', 'Par líder: oval office y white house, 805 registros', 'CRUD con relación verificado'], 6.1, 1.5, 3.4, 3.3, 18);

  // ===== 16b. Neo4j resultado =====
  s = content('Diez organizaciones acumulan el 11 % de las menciones y el 70 % se menciona una sola vez', 'Resultados',
    'Captura: pestaña Relaciones del dashboard, fecha 06/11/2026 (docs/evidencias_2026-11-16/capturas)',
    segs(slideNo + 1, 'Neo4j: resultado', SC['Neo4j: resultado']));
  img(s, 'relaciones_resumen', M, 1.4, 5.3, 3.7, 'Métricas del grafo de Neo4j: entidades únicas, concentración y cola larga');
  bullets(s, ['66 320 entidades únicas', 'Top 10: 11,3 % de las menciones', '70,3 % de las organizaciones, una sola mención'], 6.1, 1.5, 3.4, 3.3, 18);

  // ===== 17. Conciliación =====
  s = content('Las tres bases contienen el mismo número de registros en las seis fechas', 'Resultados',
    'Fuente: docs/historical_verification.json y verificacion_local.json del repositorio',
    segs(slideNo + 1, 'Resultado: conciliación', SC['Resultado: conciliación']));
  const vr = [['Fecha', 'MongoDB', 'Cassandra', 'Neo4j'].map((t, i) => ({ text: t, options: { ...TH, fontSize: 14, align: i ? 'right' : 'left' } }))];
  [['23 oct 2026', 79349], ['24 oct 2026', 47019], ['25 oct 2026', 40228], ['26 oct 2026', 71883], ['27 oct 2026', 84723], ['6 nov 2026', 80739]].forEach(([d, n], i) => {
    const f = { fill: { color: i % 2 ? K.panel : K.white } }; const t = n.toLocaleString('en-US').replace(/,/g, ' ');
    vr.push([{ text: d, options: { fontFace: F, fontSize: 14, color: K.body, ...f } }, ...[0, 1, 2].map(() => ({ text: t, options: { fontFace: F, fontSize: 14, color: K.body, align: 'right', ...f } }))]);
  });
  s.addTable(vr, { x: M, y: 1.45, w: 6.0, colW: [1.8, 1.4, 1.4, 1.4], rowH: 0.45, ...tblOpts, objectName: 'Tabla de conciliación' });
  callout(s, 'Diferencia cero\nen las 6 fechas', 6.9, 1.5, 2.6, 0.75);
  bullets(s, ['Total: 403 941', 'Conciliación en cada corrida'], 6.9, 2.6, 2.6, 2.2, 18);

  // ===== 14. KPIs =====
  s = content('Seis KPIs diarios se calculan desde MongoDB y se sirven desde Cassandra', 'Resultados',
    'Definiciones completas en la sección 9 del informe técnico. Rₜ: registros de la fecha t.',
    segs(slideNo + 1, 'KPIs', SC['KPIs']));
  const kr = [[{ text: 'KPI', options: { ...TH, fontSize: 14 } }, { text: 'Fórmula', options: { ...TH, fontSize: 14 } }, { text: '6 nov 2026', options: { ...TH, fontSize: 14, align: 'right' } }]];
  [['1 Volumen diario', 'Vₜ = |Rₜ|', '80 739'], ['2 Variación diaria', 'Δₜ = (Vₜ − Vₜ₋₁) / Vₜ₋₁ × 100', '−4,70 %'], ['3 Frecuencia de temas', 'fₜ(τ) = |{r ∈ Rₜ : τ ∈ temas(r)}|', '67 347 (TAX_FNCACT)'],
    ['4 Diversidad temática', 'Dₜ = |⋃ temas(r)|', '8 626'], ['5 Tono promedio', 'T̄ₜ = promedio de tono(r)', '−0,76'], ['6 Organizaciones', 'gₜ(o) = |{r ∈ Rₜ : o ∈ org(r)}|', '7 557 (united states)']]
    .forEach(([a, b, c], i) => { const f = { fill: { color: i % 2 ? K.panel : K.white } }; kr.push([{ text: a, options: { fontFace: F, fontSize: 14, bold: true, color: K.body, ...f } }, { text: b, options: { fontFace: F, fontSize: 14, color: K.body, ...f } }, { text: c, options: { fontFace: F, fontSize: 14, color: K.primary, bold: true, align: 'right', ...f } }]); });
  s.addTable(kr, { x: M, y: 1.45, w: 9.0, colW: [2.5, 4.0, 2.5], rowH: 0.52, ...tblOpts, objectName: 'Tabla de KPIs' });

  // ===== 18. Dashboard 1 =====
  s = content('El dashboard resume la fecha elegida y sirve los seis KPIs desde Cassandra', 'Resultados',
    'Capturas del dashboard de Streamlit, fecha 06/11/2026 (docs/evidencias_2026-11-16/capturas)',
    segs(slideNo + 1, 'Dashboard: Panorama e Indicadores', SC['Dashboard: Panorama e Indicadores']));
  img(s, 'panorama_resumen', M, 1.4, 4.4, 3.7, 'Pestaña Panorama del dashboard');
  img(s, 'indicadores_temas', 5.1, 1.4, 4.4, 3.7, 'Pestaña Indicadores: top 10 de temas');
  s.addText('Panorama', { x: M, y: 4.95, w: 4.4, h: 0.25, isTextBox: true, margin: 0, align: 'center', fontFace: F, fontSize: 12, color: K.muted });
  s.addText('Indicadores', { x: 5.1, y: 4.95, w: 4.4, h: 0.25, isTextBox: true, margin: 0, align: 'center', fontFace: F, fontSize: 12, color: K.muted });

  // ===== 20. Discusión =====
  s = content('La arquitectura responde la pregunta, con límites de escala que conviene declarar', 'Cierre', null,
    segs(slideNo + 1, 'Discusión', SC['Discusión']));
  head(s, 'Interpretación', M, 1.5, 4.3);
  bullets(s, ['Cada base cubre una consulta propia', 'La conciliación lo confirma'], M, 1.95, 4.3, 2.6);
  head(s, 'Limitaciones', 5.2, 1.5, 4.3);
  bullets(s, ['Solo seis fechas cargadas', 'Cassandra: un nodo, RF 1', 'Grafo: 10 entidades por lista'], 5.2, 1.95, 4.3, 2.9);

  // ===== 21. Conclusiones =====
  pres.addSection({ title: 'Conclusiones' });
  s = pres.addSlide({ masterName: 'CIERRE', sectionTitle: 'Conclusiones' });
  s.addText('Conclusiones', { placeholder: 'title' });
  s.addText([
    { text: '1. MongoDB: ', options: { bold: true } }, { text: 'conserva el original y su carga es idempotente.', options: { breakLine: true } },
    { text: '2. Cassandra: ', options: { bold: true } }, { text: 'sirve KPIs versionados y recuperables.', options: { breakLine: true } },
    { text: '3. Neo4j: ', options: { bold: true } }, { text: 'responde preguntas de relaciones sin joins.', options: { breakLine: true } },
    { text: '4. Airflow: ', options: { bold: true } }, { text: 'automatiza las seis etapas y las tres bases concilian.', options: { breakLine: true } },
    { text: '5. Dashboard: ', options: { bold: true } }, { text: 'seis KPIs que unen las tres bases.' },
  ], { x: M, y: 0.95, w: 9.0, h: 3.3, isTextBox: true, margin: 0, fontFace: F, fontSize: 20, color: K.white, valign: 'top', paraSpaceAfter: 12 });
  s.addText('Código y evidencias: github.com/KarolayTamayoH/global-news-intelligence', { x: M, y: 4.5, w: 9.0, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 15, color: 'A0BBDD' });
  s.addText('¿Hay preguntas o comentarios?', { x: M, y: 4.9, w: 9.0, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 15, color: 'A0BBDD' });
  slideNo++;
  s.addNotes(segs(slideNo + 0, 'Conclusiones', SC['Conclusiones']));

  // ===== Referencias =====
  pres.addSection({ title: 'Referencias' });
  s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Referencias' });
  s.addText('Referencias', { placeholder: 'title' });
  const refs = [
    'Apache Software Foundation. (2026). Apache Airflow 2.11.1 documentation. https://airflow.apache.org/docs/apache-airflow/2.11.1/',
    'Apache Software Foundation. (2026). Apache Cassandra documentation. https://cassandra.apache.org/doc/latest/',
    'Leetaru, K., & Schrodt, P. A. (2013). GDELT: Global Data on Events, Location and Tone, 1979–2012. ISA Annual Convention. https://www.gdeltproject.org/',
    'MongoDB, Inc. (2026). MongoDB manual. https://www.mongodb.com/docs/manual/',
    'Neo4j, Inc. (2026). Neo4j Cypher manual. https://neo4j.com/docs/cypher-manual/current/',
    'Streamlit Inc. (2026). Streamlit documentation. https://docs.streamlit.io/',
    'Tamayo, M. K., et al. (2026). Global News Intelligence [Código fuente]. https://github.com/KarolayTamayoH/global-news-intelligence',
  ];
  s.addText(refs.map((r, i) => ({ text: r, options: { breakLine: i < refs.length - 1 } })), { x: M, y: 1.0, w: 9.0, h: 4.2, isTextBox: true, margin: 0, fontFace: F, fontSize: 13, color: K.body, valign: 'top', paraSpaceAfter: 8 });
  s.addNotes('Referencias completas de todas las fuentes citadas. Esta diapositiva no se narra en el video.');

  // ===== Apéndices =====
  pres.addSection({ title: 'Apéndice' });
  s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Apéndice' });
  s.addText('Apéndice A: el CRUD funciona en las tres bases y Cassandra se recupera tras reiniciar', { placeholder: 'title' });
  const ar = [['Prueba', 'MongoDB', 'Cassandra', 'Neo4j'].map(t => ({ text: t, options: { ...TH, fontSize: 16 } }))];
  [['Crear', 'Sí', 'Sí', 'Sí'], ['Leer', 'Sí', 'Sí', 'Sí'], ['Actualizar', 'Sí', 'Sí', 'Sí'], ['Borrar', 'Sí', 'Sí', 'Sí'], ['Relación (crear y borrar)', '—', '—', 'Sí']].forEach((r, i) => {
    const f = { fill: { color: i % 2 ? K.panel : K.white } };
    ar.push(r.map((t, j) => ({ text: t, options: { fontFace: F, fontSize: 16, color: K.body, align: j ? 'center' : 'left', ...f } })));
  });
  s.addTable(ar, { x: M, y: 1.5, w: 7.0, colW: [2.8, 1.4, 1.5, 1.3], rowH: 0.5, ...tblOpts, objectName: 'Tabla CRUD' });
  s.addText('Fuente: docs/crud_verification.json y docs/cassandra_recovery_verification.json', { x: M, y: 5.2, w: 8.3, h: 0.3, isTextBox: true, margin: 0, fontFace: F, fontSize: 12, color: K.muted });
  s.addNotes('Pregunta anticipada: ¿está probado el CRUD? Sí, en las tres bases, con eliminación de los datos de prueba. La recuperación de Cassandra tras reiniciar también está verificada. Responde: Caroline (MongoDB), Mayra (Cassandra) o Fabricio (Neo4j) según la base.');

  s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Apéndice' });
  s.addText('Apéndice B: guardar todo en una sola base obligaría a perder consultas o a recalcular', { placeholder: 'title' });
  const br = [['Base única', 'Qué se pierde'].map(t => ({ text: t, options: { ...TH, fontSize: 16 } }))];
  [['Solo MongoDB', 'Recorrido de relaciones y lecturas versionadas'], ['Solo Cassandra', 'Documento original y consultas ad hoc'], ['Solo Neo4j', 'Agregados diarios baratos y esquema validado']].forEach((r, i) => {
    const f = { fill: { color: i % 2 ? K.panel : K.white } };
    br.push(r.map(t => ({ text: t, options: { fontFace: F, fontSize: 18, color: K.body, ...f } })));
  });
  s.addTable(br, { x: M, y: 1.6, w: 9.0, colW: [2.8, 6.2], rowH: [0.45, 0.8, 0.8, 0.8], ...tblOpts, objectName: 'Tabla de alternativas' });
  s.addNotes('Pregunta anticipada: ¿por qué no usar solo una base? Cada alternativa pierde una de las tres consultas que el proyecto necesita. Responde Abel o quien tenga la palabra.');

  s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Apéndice' });
  s.addText('Apéndice C: el dashboard muestra el DAG de ocho tareas y su ejecución completa', { placeholder: 'title' });
  img(s, 'panorama_flujo', M, 1.5, 9.0, 3.4, 'Diagrama del DAG de Airflow mostrado en la pestaña Panorama del dashboard');
  s.addText('Fuente: pestaña Panorama del dashboard, sección «Cómo viajan los datos» (docs/evidencias_2026-11-16/capturas)', { x: M, y: 5.2, w: 8.3, h: 0.3, isTextBox: true, margin: 0, fontFace: F, fontSize: 12, color: K.muted });
  s.addNotes('Apoyo para la diapositiva del DAG: es el mismo diagrama que dibuja el dashboard, con las ocho tareas y la rama paralela de Cassandra y Neo4j.');

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  require('fs').writeFileSync(OUT.replace(/\.pptx$/, '_guion.json'), JSON.stringify({ GUION, TOTALS, total: clock.t }, null, 1), 'utf-8');
  console.log('ok', mmss(clock.t), JSON.stringify(Object.fromEntries(Object.entries(TOTALS).map(([k, v]) => [NAMES[k], mmss(v)]))));
})().catch(e => { console.error(e); process.exit(1); });
