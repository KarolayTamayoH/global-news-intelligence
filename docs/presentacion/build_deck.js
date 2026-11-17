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
function content(title, section, cite, notes) {
  pres.addSection({ title: section + ': ' + title.slice(0, 30) });
  const s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: section + ': ' + title.slice(0, 30) });
  breadcrumb(s, section);
  s.addText(title, { placeholder: 'title' });
  if (cite) s.addText(cite, { x: M, y: 5.2, w: 8.3, h: 0.3, isTextBox: true, margin: 0, fontFace: F, fontSize: 12, color: K.muted, valign: 'middle', objectName: 'Cita' });
  s.addNotes(notes);
  return s;
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

(async () => {
  // ===== 1. Portada =====
  pres.addSection({ title: 'Portada' });
  let s = pres.addSlide({ masterName: 'PORTADA', sectionTitle: 'Portada' });
  s.addText('Tres bases de datos con roles distintos mantienen conciliadas 403 941 noticias de GDELT', { x: 0.7, y: 1.2, w: 8.6, h: 1.8, isTextBox: true, margin: 0, fontFace: F, fontSize: 32, bold: true, color: K.white, valign: 'top', align: 'left' });
  s.addText('Global News Intelligence: pipeline automatizado con MongoDB, Cassandra y Neo4j', { x: 0.7, y: 3.2, w: 8.6, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 16, color: K.soft });
  s.addText('Equipo Global News Intelligence  ·  Universidad de Ingeniería y Tecnología (UTEC)', { x: 0.7, y: 3.8, w: 8.6, h: 0.35, isTextBox: true, margin: 0, fontFace: F, fontSize: 15, color: 'CADCFC' });
  s.addText('Proyecto 2, curso de Big Data  ·  Noviembre de 2026', { x: 0.7, y: 4.2, w: 8.6, h: 0.35, isTextBox: true, margin: 0, fontFace: F, fontSize: 15, color: 'CADCFC' });
  s.addNotes('Presentación del equipo. El mensaje central: cada base de datos resuelve un patrón de acceso distinto, y un pipeline en Airflow las mantiene conciliadas. Duración: 30 segundos.');

  // ===== 2. Motivación =====
  s = content('GDELT publica cientos de miles de registros por día y una sola base no responde todas las consultas', 'Contexto',
    'GDELT Project; Leetaru y Schrodt (2013)',
    'Situación: GDELT es un flujo diario de datos semiestructurados sobre noticias del mundo. Complicación: el mismo dato se necesita para tres usos que piden modelos distintos. Conservar el original sin pérdida, servir indicadores diarios con baja latencia y explorar qué temas y organizaciones aparecen juntos. En la carga real hay 403 941 registros en seis fechas.');
  bullets(s, ['Cada día llegan 40 000 a 85 000 registros', 'Hay que conservar el original', 'Los indicadores deben responder rápido', 'Las relaciones piden recorrer un grafo'], M, 1.5, 5.2, 3.4);
  s.addShape(pres.ShapeType.roundRect, { x: 6.2, y: 1.5, w: 3.3, h: 3.2, rectRadius: 0.06, fill: { color: K.panel }, line: { color: K.rule, width: 0.75 }, objectName: 'Panel de cifra' });
  s.addText('403 941', { x: 6.2, y: 1.9, w: 3.3, h: 0.9, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 44, bold: true, color: K.primary });
  s.addText('registros GKG en seis fechas, del 23 de octubre al 6 de noviembre de 2026', { x: 6.45, y: 2.9, w: 2.8, h: 1.2, isTextBox: true, margin: 0, align: 'center', valign: 'top', fontFace: F, fontSize: 16, color: K.body });

  // ===== 3. Pregunta =====
  s = content('Este proyecto pregunta qué base de datos conviene a cada tipo de dato y si el flujo puede automatizarse', 'Contexto',
    null,
    'La pregunta de investigación del proyecto. Tiene dos partes: una de modelado, qué dato va en qué base y por qué, y una de ingeniería, si todo el flujo puede correr solo cada día y terminar con las tres bases conciliadas.');
  s.addShape(pres.ShapeType.roundRect, { x: 1.0, y: 1.6, w: 8.0, h: 1.7, rectRadius: 0.1, fill: { color: 'EBF3FA' }, line: { color: K.accent, width: 1.5 }, objectName: 'Pregunta' });
  s.addText('¿Qué base resuelve mejor documentos, indicadores y relaciones de GDELT, y puede un DAG de Airflow mantenerlas conciliadas cada día?', { x: 1.25, y: 1.7, w: 7.5, h: 1.5, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 22, color: K.primary });
  s.addText([{ text: 'Aporte: ', options: { bold: true } }, { text: 'pipeline de extremo a extremo con seis KPIs y un dashboard que consulta las tres bases.' }],
    { x: M, y: 3.7, w: 9.0, h: 1.0, isTextBox: true, margin: 0, fontFace: F, fontSize: 20, color: K.body, valign: 'top' });

  // ===== 4. Datos =====
  s = content('El GKG diario aporta 11 columnas por registro y temas, organizaciones y tono concentran la señal', 'Datos',
    'Fuente: GDELT GKG diario, formato CSV tabulado dentro de ZIP (Leetaru y Schrodt, 2013)',
    'El Global Knowledge Graph de GDELT entrega un archivo por día con once columnas. Tres de ellas alimentan los KPIs y el grafo: THEMES, ORGANIZATIONS y TONE. La validación comprueba el esquema exacto, el formato de fecha y que el tono sea numérico. En la muestra de 83 729 registros no hubo registros mal formados.');
  const dr = [[{ text: 'Campo', options: { ...TH, fontSize: 16 } }, { text: 'Contenido', options: { ...TH, fontSize: 16 } }]];
  [['DATE', 'Fecha de publicación', false], ['THEMES', 'Lista de temas', true], ['ORGANIZATIONS', 'Lista de organizaciones', true], ['TONE', 'Tono del registro', true], ['Otros 7 campos', 'Personas, ubicaciones, URL', false]]
    .forEach(([a, b, key], i) => { const f = { fill: { color: key ? 'DCEBF8' : (i % 2 ? K.panel : K.white) } }; dr.push([{ text: a, options: { fontFace: F, fontSize: 16, bold: key, color: K.body, ...f } }, { text: b, options: { fontFace: F, fontSize: 16, color: K.body, ...f } }]); });
  s.addTable(dr, { x: M, y: 1.5, w: 5.6, colW: [2.2, 3.4], rowH: 0.5, ...tblOpts, objectName: 'Tabla de campos' });
  s.addText('Los tres campos resaltados alimentan los KPIs y el grafo', { x: M, y: 4.6, w: 5.6, h: 0.35, isTextBox: true, margin: 0, fontFace: F, fontSize: 14, color: K.muted });
  head(s, 'Controles', 6.5, 1.5, 3.0);
  bullets(s, ['Esquema de 11 columnas', 'Fecha válida', 'Tono numérico', 'Muestra: 0 registros mal formados'], 6.5, 1.95, 3.0, 2.9, 18);

  // ===== 5. Arquitectura =====
  s = content('Airflow orquesta un flujo único que va de GDELT a tres bases y termina en un dashboard', 'Diseño',
    'Docker Compose: MongoDB 8.0, Cassandra 5.0, Neo4j 5.26, Airflow 2.11, Streamlit 1.66',
    'Arquitectura. Airflow ejecuta ocho tareas. MongoDB recibe primero los documentos y es la fuente de verdad. Cassandra y Neo4j se alimentan desde Mongo en paralelo. Streamlit lee de las tres bases. Todo corre en contenedores con Docker Compose.');
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
    'Esta es la justificación técnica pedida. El criterio es el patrón de acceso. Un registro completo y variable pide un documento: MongoDB. Un agregado por fecha leído muchas veces pide una tabla diseñada por consulta: Cassandra. Una relación entre registro, tema y organización pide recorrer aristas: Neo4j. Una sola base obligaría a recalcular agregados en cada consulta o a perder el recorrido de relaciones.');
  const jr = [[{ text: 'Dato', options: { ...TH, fontSize: 16 } }, { text: 'Base', options: { ...TH, fontSize: 16 } }, { text: 'Motivo', options: { ...TH, fontSize: 16 } }]];
  [['Registro GKG completo', 'MongoDB', 'Esquema flexible y upsert idempotente'], ['KPIs diarios y rankings', 'Cassandra', 'Lectura por fecha y versiones'], ['Temas y organizaciones por registro', 'Neo4j', 'Recorrido de aristas sin joins']]
    .forEach(([a, b, c], i) => { const f = { fill: { color: i % 2 ? K.panel : K.white } }; jr.push([{ text: a, options: { fontFace: F, fontSize: 18, color: K.body, ...f } }, { text: b, options: { fontFace: F, fontSize: 18, bold: true, color: K.primary, ...f } }, { text: c, options: { fontFace: F, fontSize: 18, color: K.body, ...f } }]); });
  s.addTable(jr, { x: M, y: 1.6, w: 9.0, colW: [3.4, 1.7, 3.9], rowH: [0.45, 0.8, 0.8, 0.8], ...tblOpts, objectName: 'Tabla de justificación' });

  // ===== 7. DAG =====
  s = content('Un DAG de ocho tareas cubre las seis etapas exigidas y se ejecuta cada día a las 06:00', 'Diseño',
    'Apache Airflow 2.11.1, API TaskFlow (Apache Software Foundation, 2026)',
    'El DAG usa la API TaskFlow. Se fija la fecha, se extrae, se valida y se transforma. Luego se carga MongoDB. Cassandra y Neo4j corren en paralelo y la última tarea concilia las tres bases. Programación cron 0 6 * * *, dos reintentos con cinco minutos de espera, sin catchup. La ejecución programada del 6 de noviembre quedó verificada con 80 739 registros.');
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
  s.addShape(pres.ShapeType.line, { x: 7.9, y: 3.05, w: 0.25, h: 0, line: { color: K.muted, width: 1.5 }, objectName: 'Conector' });
  s.addShape(pres.ShapeType.line, { x: 7.9, y: 3.85, w: 0.25, h: 0, line: { color: K.muted, width: 1.5 }, objectName: 'Conector' });
  s.addShape(pres.ShapeType.line, { x: 8.15, y: 3.05, w: 0, h: 0.8, line: { color: K.muted, width: 1.5 }, objectName: 'Conector' });
  s.addShape(pres.ShapeType.line, { x: 8.15, y: 3.45, w: 0.15, h: 0, line: { color: K.muted, width: 1.5, endArrowType: 'triangle' }, objectName: 'Flecha' });
  s.addShape(pres.ShapeType.roundRect, { x: 8.3, y: 3.05, w: 1.2, h: 0.8, rectRadius: 0.06, fill: { color: K.primary }, line: { color: K.primary }, objectName: 'Tarea generate_indicators' });
  s.addText('generate_\nindicators', { x: 8.3, y: 3.05, w: 1.2, h: 0.8, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 11, bold: true, color: K.white });
  bullets(s, ['Cron diario 0 6 * * *', '2 reintentos, 5 minutos', 'Sin catchup'], M, 2.75, 4.8, 1.8, 18);

  // ===== 8. MongoDB =====
  s = content('MongoDB conserva el registro original y hace idempotente la carga de cada fecha', 'Diseño',
    'MongoDB, Inc. (2026), manual de MongoDB',
    'Modelo de MongoDB. gkg_records guarda un documento por registro, con las listas ya separadas. La carga usa upsert con setOnInsert, de modo que repetir una fecha no duplica documentos. Hay un validador JSON Schema y dos colecciones de historial para auditar la ingesta y el estado de cada etapa del DAG.');
  [['gkg_records', 'Un documento por registro'], ['ingestion_history', 'Un documento por archivo'], ['pipeline_history', 'Estado por etapa del DAG']].forEach(([n, d], i) => {
    const y = 1.5 + i * 1.15;
    s.addShape(pres.ShapeType.roundRect, { x: M, y, w: 4.8, h: 1.0, rectRadius: 0.06, fill: { color: K.panel }, line: { color: K.accent, width: 1.25 }, objectName: 'Colección ' + n });
    s.addText(n, { x: M + 0.2, y: y + 0.1, w: 4.4, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 18, bold: true, color: K.primary, valign: 'middle' });
    s.addText(d, { x: M + 0.2, y: y + 0.5, w: 4.4, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 16, color: K.body, valign: 'middle' });
  });
  bullets(s, ['Upsert por _id: repetir una fecha no duplica', 'Validador JSON Schema', 'Índices por fecha y archivo'], 5.6, 1.5, 3.9, 3.3);

  // ===== 9. Cassandra =====
  s = content('Cassandra publica cada KPI como una versión inmutable que se consulta por fecha', 'Diseño',
    'Apache Software Foundation (2026), documentación de Apache Cassandra',
    'Modelo de Cassandra. Una tabla por consulta: métricas diarias, temas y organizaciones por fecha. Para no mostrar datos a medias, cada publicación escribe una versión con un UUID de generación y solo al final se activa. La consistencia es LOCAL_QUORUM. La recuperación tras reiniciar quedó verificada.');
  [['1', 'Escribir versión nueva'], ['2', 'Verificar conteos'], ['3', 'Activar la generación']].forEach(([n, t], i) => {
    const y = 1.5 + i * 1.15;
    s.addShape(pres.ShapeType.roundRect, { x: M, y, w: 4.8, h: 0.9, rectRadius: 0.06, fill: { color: i === 2 ? K.primary : K.accent }, line: { color: K.accent }, objectName: 'Paso ' + n });
    s.addText(n + '. ' + t, { x: M + 0.2, y, w: 4.4, h: 0.9, isTextBox: true, margin: 0, fontFace: F, fontSize: 18, bold: true, color: K.white, valign: 'middle' });
    if (i < 2) arrow(s, M + 2.4, y + 0.9, M + 2.4, y + 1.15);
  });
  bullets(s, ['Una tabla por consulta de KPI', 'Lectura por partición de fecha', 'Consistencia LOCAL_QUORUM'], 5.6, 1.5, 3.9, 3.3);

  // ===== 10. Neo4j =====
  s = content('Neo4j conecta registros, temas y organizaciones con unos 4,5 millones de aristas', 'Diseño',
    'Neo4j, Inc. (2026), manual de Cypher',
    'Modelo de grafo. Tres tipos de nodos: GKGRecord, Theme y Organization. Dos relaciones: HAS_THEME y MENTIONS_ORG. Para acotar el tamaño se enlazan las diez primeras entidades de cada lista, y las cargas usan MERGE en lotes de cien. Entre las seis fechas suman unos 3,4 millones de aristas de temas y 1,1 millones de organizaciones.');
  [['Theme', 0.5, K.accent], ['GKGRecord', 2.55, K.primary], ['Organization', 4.6, K.accent]].forEach(([t, x, c]) => {
    s.addShape(pres.ShapeType.ellipse, { x, y: 2.3, w: 1.4, h: 1.1, fill: { color: c }, line: { color: c }, objectName: 'Nodo ' + t });
    s.addText(t, { x, y: 2.3, w: 1.4, h: 1.1, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 14, bold: true, color: K.white });
  });
  arrow(s, 2.55, 2.85, 1.9, 2.85); arrow(s, 3.95, 2.85, 4.6, 2.85);
  s.addText('HAS_THEME', { x: 1.0, y: 3.5, w: 1.6, h: 0.3, isTextBox: true, margin: 0, align: 'center', fontFace: F, fontSize: 12, color: K.muted });
  s.addText('MENTIONS_ORG', { x: 3.5, y: 3.5, w: 1.8, h: 0.3, isTextBox: true, margin: 0, align: 'center', fontFace: F, fontSize: 12, color: K.muted });
  s.addText('Esquema del grafo', { x: M, y: 4.2, w: 5.1, h: 0.3, isTextBox: true, margin: 0, fontFace: F, fontSize: 14, color: K.muted });
  bullets(s, ['3,4 M de aristas HAS_THEME', '1,1 M de aristas MENTIONS_ORG', 'Diez entidades por lista'], 6.2, 1.5, 3.3, 3.3, 18);

  // ===== 11. KPIs =====
  s = content('Seis KPIs diarios se calculan desde MongoDB y se sirven desde Cassandra', 'Resultados',
    'Definiciones completas en la sección 9 del informe técnico. Rₜ: registros de la fecha t.',
    'Los seis indicadores. Volumen, variación respecto de la fecha anterior, frecuencia de temas, diversidad temática, tono promedio y organizaciones más mencionadas. Todos se calculan en la etapa de agregación y se reconcilian con las tres bases. Valores del 6 de noviembre de 2026.');
  const kr = [[{ text: 'KPI', options: { ...TH, fontSize: 14 } }, { text: 'Fórmula', options: { ...TH, fontSize: 14 } }, { text: '6 nov 2026', options: { ...TH, fontSize: 14, align: 'right' } }]];
  [['1 Volumen diario', 'Vₜ = |Rₜ|', '80 739'], ['2 Variación diaria', 'Δₜ = (Vₜ − Vₜ₋₁) / Vₜ₋₁ × 100', '−4,70 %'], ['3 Frecuencia de temas', 'fₜ(τ) = |{r ∈ Rₜ : τ ∈ temas(r)}|', '67 347 (TAX_FNCACT)'],
    ['4 Diversidad temática', 'Dₜ = |⋃ temas(r)|', '8 626'], ['5 Tono promedio', 'T̄ₜ = promedio de tono(r)', '−0,76'], ['6 Organizaciones', 'gₜ(o) = |{r ∈ Rₜ : o ∈ org(r)}|', '7 557 (united states)']]
    .forEach(([a, b, c], i) => { const f = { fill: { color: i % 2 ? K.panel : K.white } }; kr.push([{ text: a, options: { fontFace: F, fontSize: 14, bold: true, color: K.body, ...f } }, { text: b, options: { fontFace: F, fontSize: 14, color: K.body, ...f } }, { text: c, options: { fontFace: F, fontSize: 14, color: K.primary, bold: true, align: 'right', ...f } }]); });
  s.addTable(kr, { x: M, y: 1.45, w: 9.0, colW: [2.5, 4.0, 2.5], rowH: 0.52, ...tblOpts, objectName: 'Tabla de KPIs' });

  // ===== 12. Resultado volumen =====
  s = content('El volumen cae 49 % durante el fin de semana del 24 y 25 de octubre y se recupera el lunes', 'Resultados',
    'Fuente: conteos de gkg_records en MongoDB por fecha de publicación del GKG',
    'Resultado uno. El 23 de octubre hay 79 349 registros. El sábado 24 baja a 47 019, una caída de 40,7 por ciento, y el domingo 25 a 40 228. El lunes 26 sube a 71 883 y el 27 a 84 723. Es un patrón semanal esperable en la producción de noticias.');
  s.addChart(pres.charts.BAR, [{ name: 'Registros', labels, values: [79349, 47019, 40228, 71883, 84723, 80739] }], {
    x: M, y: 1.4, w: 5.4, h: 3.7, barDir: 'col', chartColors: [K.grey, K.accent, K.primary, K.grey, K.grey, K.grey],
    showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '#,##0', dataLabelFontSize: 12, valAxisMaxVal: 100000, valAxisLabelFormatCode: '#,##0', ...chartBase,
    showValAxisTitle: true, valAxisTitle: 'Registros', valAxisTitleColor: K.muted, valAxisTitleFontSize: 14, objectName: 'Gráfico de volumen',
  });
  callout(s, '−49 %\nfrente al 23 oct', 2.55, 1.45, 1.45, 0.65);
  bullets(s, ['Sábado 24: 47 019', 'Domingo 25: 40 228', 'Lunes 26: 71 883'], 6.2, 1.5, 3.3, 3.3, 18);

  // ===== 13. Resultado tono =====
  s = content('El tono promedio es negativo en todas las fechas y toca su mínimo cuando el volumen es menor', 'Resultados',
    'Fuente: KPI 5, tono promedio por fecha, publicado en Cassandra',
    'Resultado dos. El tono promedio de GDELT es negativo en las seis fechas, entre menos 0,66 y menos 1,12. El mínimo, menos 1,12, coincide con el domingo 25, el día de menor volumen. Con pocos registros el promedio pesa más cada noticia negativa.');
  s.addChart(pres.charts.LINE, [{ name: 'Tono promedio', labels, values: [-0.83, -1.06, -1.12, -0.67, -0.66, -0.76] }], {
    x: M, y: 1.4, w: 5.4, h: 3.7, chartColors: [K.accent], lineSize: 3, lineDataSymbolSize: 9,
    showValue: true, dataLabelPosition: 't', dataLabelFormatCode: '0.00', dataLabelFontSize: 12, valAxisMinVal: -1.4, valAxisMaxVal: -0.4, valAxisLabelFormatCode: '0.0', ...chartBase,
    showValAxisTitle: true, valAxisTitle: 'Tono promedio', valAxisTitleColor: K.muted, valAxisTitleFontSize: 14, objectName: 'Gráfico de tono',
  });
  callout(s, 'Mínimo: −1,12 (25 oct)', 3.0, 3.85, 2.3, 0.45);
  bullets(s, ['Rango: −1,12 a −0,66', 'Mínimo el 25 oct', 'Mayor volumen, tono menos negativo'], 6.2, 1.5, 3.3, 3.3, 18);

  // ===== 14. Conciliación =====
  s = content('Las tres bases contienen el mismo número de registros en las seis fechas', 'Resultados',
    'Fuente: docs/historical_verification.json y verificacion_local.json del repositorio',
    'Resultado tres. Para cada fecha se comparan los registros en MongoDB, Cassandra y Neo4j y deben coincidir. Coinciden en las seis fechas y suman 403 941 registros. La última tarea del DAG ejecuta esta conciliación en cada corrida.');
  const vr = [['Fecha', 'MongoDB', 'Cassandra', 'Neo4j'].map((t, i) => ({ text: t, options: { ...TH, fontSize: 14, align: i ? 'right' : 'left' } }))];
  [['23 oct 2026', 79349], ['24 oct 2026', 47019], ['25 oct 2026', 40228], ['26 oct 2026', 71883], ['27 oct 2026', 84723], ['6 nov 2026', 80739]].forEach(([d, n], i) => {
    const f = { fill: { color: i % 2 ? K.panel : K.white } }; const t = n.toLocaleString('en-US').replace(/,/g, ' ');
    vr.push([{ text: d, options: { fontFace: F, fontSize: 14, color: K.body, ...f } }, ...[0, 1, 2].map(() => ({ text: t, options: { fontFace: F, fontSize: 14, color: K.body, align: 'right', ...f } }))]);
  });
  s.addTable(vr, { x: M, y: 1.45, w: 6.0, colW: [1.8, 1.4, 1.4, 1.4], rowH: 0.45, ...tblOpts, objectName: 'Tabla de conciliación' });
  callout(s, 'Diferencia cero\nen las 6 fechas', 6.9, 1.5, 2.6, 0.75);
  bullets(s, ['Total: 403 941', 'Conciliación en cada corrida'], 6.9, 2.6, 2.6, 2.2, 18);

  // ===== 15. Dashboard =====
  s = content('El dashboard de Streamlit consulta las tres bases en cuatro vistas', 'Resultados',
    'Streamlit Inc. (2026), documentación de Streamlit',
    'Aquí se pasa a la demostración en vivo del dashboard, en localhost puerto 8501. Panorama resume la fecha. Indicadores muestra los seis KPIs desde Cassandra. Documentos consulta MongoDB. Relaciones dibuja el grafo de Neo4j. Mostrar el cambio de fecha y la lectura de un documento.');
  [['Panorama', 'Resumen de la fecha', K.primary], ['Indicadores', 'Seis KPIs desde Cassandra', K.accent], ['Documentos', 'Búsqueda en MongoDB', K.accent], ['Relaciones', 'Grafo desde Neo4j', K.accent]].forEach(([t, d, c], i) => {
    const x = M + i * 2.28;
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.6, w: 2.1, h: 2.0, rectRadius: 0.06, fill: { color: c }, line: { color: c }, objectName: 'Vista ' + t });
    s.addText(t, { x, y: 1.85, w: 2.1, h: 0.5, isTextBox: true, margin: 0, align: 'center', valign: 'middle', fontFace: F, fontSize: 18, bold: true, color: K.white });
    s.addText(d, { x: x + 0.15, y: 2.45, w: 1.8, h: 0.9, isTextBox: true, margin: 0, align: 'center', valign: 'top', fontFace: F, fontSize: 14, color: 'E6EEF8' });
  });
  s.addText('Demostración en vivo en localhost:8501', { x: M, y: 4.1, w: 9.0, h: 0.45, isTextBox: true, margin: 0, fontFace: F, fontSize: 20, bold: true, color: K.primary });

  // ===== 16. Discusión =====
  s = content('La arquitectura responde la pregunta, con límites de escala que conviene declarar', 'Cierre',
    null,
    'Discusión. Interpretación: cada base responde una consulta que las otras no resuelven bien, y la conciliación demuestra que el pipeline las mantiene consistentes. Limitaciones: solo hay seis fechas, Cassandra corre con factor de replicación uno en un nodo y el grafo se acota a diez entidades por lista para controlar su tamaño. Son decisiones del entorno local del curso, no de la arquitectura.');
  head(s, 'Interpretación', M, 1.5, 4.3);
  bullets(s, ['Cada base cubre una consulta propia', 'La conciliación lo confirma'], M, 1.95, 4.3, 2.6);
  head(s, 'Limitaciones', 5.2, 1.5, 4.3);
  bullets(s, ['Solo seis fechas cargadas', 'Cassandra: un nodo, RF 1', 'Grafo: 10 entidades por lista'], 5.2, 1.95, 4.3, 2.9);

  // ===== 17. Conclusiones =====
  pres.addSection({ title: 'Conclusiones' });
  s = pres.addSlide({ masterName: 'CIERRE', sectionTitle: 'Conclusiones' });
  s.addText('Conclusiones', { placeholder: 'title' });
  s.addText([
    { text: '1. Cada base resuelve un patrón distinto: ', options: { bold: true } }, { text: 'documentos, KPIs por fecha y relaciones.', options: { breakLine: true } },
    { text: '2. El DAG automatiza las seis etapas: ', options: { bold: true } }, { text: 'de la descarga a los indicadores.', options: { breakLine: true } },
    { text: '3. Las tres bases concilian: ', options: { bold: true } }, { text: '403 941 registros, diferencia cero.' },
  ], { x: M, y: 1.0, w: 9.0, h: 3.0, isTextBox: true, margin: 0, fontFace: F, fontSize: 22, color: K.white, valign: 'top', paraSpaceAfter: 18 });
  s.addText('Código y evidencias: github.com/KarolayTamayoH/global-news-intelligence', { x: M, y: 4.5, w: 9.0, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 15, color: 'A0BBDD' });
  s.addText('¿Hay preguntas o comentarios?', { x: M, y: 4.9, w: 9.0, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 15, color: 'A0BBDD' });
  s.addNotes('Cierre. Esta diapositiva se queda en pantalla durante las preguntas. Repetir el mensaje: cada base resuelve un patrón de acceso distinto y el pipeline las mantiene conciliadas.');

  // ===== 18. Referencias =====
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
  s.addNotes('Referencias completas de todas las fuentes citadas en la presentación.');

  // ===== Apéndice A =====
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
  s.addNotes('Pregunta anticipada: ¿está probado el CRUD? Sí, en las tres bases, con eliminación de los datos de prueba. La recuperación de Cassandra tras reiniciar también está verificada.');

  // ===== Apéndice B =====
  s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Apéndice' });
  s.addText('Apéndice B: guardar todo en una sola base obligaría a perder consultas o a recalcular', { placeholder: 'title' });
  const br = [['Base única', 'Qué se pierde'].map(t => ({ text: t, options: { ...TH, fontSize: 16 } }))];
  [['Solo MongoDB', 'Recorrido de relaciones y lecturas versionadas'], ['Solo Cassandra', 'Documento original y consultas ad hoc'], ['Solo Neo4j', 'Agregados diarios baratos y esquema validado']].forEach((r, i) => {
    const f = { fill: { color: i % 2 ? K.panel : K.white } };
    br.push(r.map(t => ({ text: t, options: { fontFace: F, fontSize: 18, color: K.body, ...f } })));
  });
  s.addTable(br, { x: M, y: 1.6, w: 9.0, colW: [2.8, 6.2], rowH: [0.45, 0.8, 0.8, 0.8], ...tblOpts, objectName: 'Tabla de alternativas' });
  s.addNotes('Pregunta anticipada: ¿por qué no usar solo una base? Cada alternativa pierde una de las tres consultas que el proyecto necesita.');

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('ok');
})().catch(e => { console.error(e); process.exit(1); });
