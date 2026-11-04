/* Capturas de la aplicacion real. Requiere Playwright y Chrome local. */
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const output = path.resolve(__dirname, '../docs/capturas');
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1150 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  try {
    await page.goto('http://127.0.0.1:8501', { waitUntil: 'domcontentloaded' });
    const indicators = page.getByRole('tab', { name: 'Indicadores · Cassandra', exact: true });
    await indicators.waitFor({ timeout: 90000 });
    await page.locator('[data-testid="stPlotlyChart"]').first().waitFor({ timeout: 90000 });
    await page.waitForTimeout(1200);
    const line = await page.locator('[data-testid="stPlotlyChart"]').nth(0).boundingBox();
    await page.screenshot({ path: path.join(output, 'panorama.png'),
      clip: { x: 0, y: 0, width: 1440, height: Math.min(1150, Math.ceil(line.y + line.height + 20)) } });
    const diversity = page.getByRole('heading', { name: 'Diversidad tematica y tono informativo', exact: true });
    await diversity.evaluate(element => { element.style.scrollMarginTop = '75px'; element.scrollIntoView({ block: 'start' }); });
    const headingBox = await diversity.boundingBox();
    const toneBox = await page.locator('[data-testid="stPlotlyChart"]').nth(3).boundingBox();
    await page.screenshot({ path: path.join(output, 'indicadores.png'), clip: {
      x: 0, y: Math.max(0, Math.floor(headingBox.y - 10)), width: 1440,
      height: Math.ceil(toneBox.y + toneBox.height - headingBox.y + 35) } });
    for (const [title, chartIndex, filename] of [
      ['Top 10 temas mas mencionados', 1, 'temas.png'],
      ['Top 10 entidades organizacionales', 4, 'organizaciones.png'],
    ]) {
      const heading = page.getByRole('heading', { name: title, exact: true });
      await heading.evaluate(element => { element.style.scrollMarginTop = '75px'; element.scrollIntoView({ block: 'start' }); });
      const headingBox = await heading.boundingBox();
      const chartBox = await page.locator('[data-testid="stPlotlyChart"]').nth(chartIndex).boundingBox();
      await page.screenshot({ path: path.join(output, filename), clip: {
        x: Math.max(0, Math.floor(headingBox.x - 24)), y: Math.max(0, Math.floor(headingBox.y - 10)),
        width: 1008, height: Math.ceil(chartBox.y + chartBox.height - headingBox.y + 30) } });
    }
    await page.getByRole('tab', { name: 'Documentos · MongoDB', exact: true }).click();
    await page.getByRole('heading', { name: 'Explorador documental', exact: true }).waitFor();
    await page.getByRole('heading', { name: 'Global News Intelligence', exact: false }).evaluate(element => element.scrollIntoView({ block: 'start' }));
    await page.waitForTimeout(700);
    const documentsHeading = await page.getByRole('heading', { name: 'Explorador documental', exact: true }).boundingBox();
    const documentJson = await page.locator('[data-testid="stJson"]').boundingBox();
    await page.screenshot({ path: path.join(output, 'documentos.png'), clip: {
      x: Math.max(0, Math.floor(documentsHeading.x - 24)), y: Math.floor(documentsHeading.y - 12),
      width: 1008, height: Math.min(1150 - Math.floor(documentsHeading.y - 12),
        Math.ceil(documentJson.y + documentJson.height - documentsHeading.y + 35)) } });
    await page.setViewportSize({ width: 1440, height: 1550 });
    await page.getByRole('tab', { name: 'Relaciones · Neo4j', exact: true }).click();
    await page.getByRole('heading', { name: 'Explorador de relaciones', exact: true }).waitFor();
    await page.waitForTimeout(700);
    const graphHeading = await page.getByRole('heading', { name: 'Explorador de relaciones', exact: true }).boundingBox();
    const graphBox = await page.locator('[data-testid="stPlotlyChart"]').last().boundingBox();
    await page.screenshot({ path: path.join(output, 'relaciones.png'), clip: {
      x: Math.max(0, Math.floor(graphHeading.x - 24)), y: Math.floor(graphHeading.y - 12), width: 1008,
      height: Math.ceil(graphBox.y + graphBox.height - graphHeading.y + 95) } });
    const screenshots = ['panorama.png', 'indicadores.png', 'temas.png', 'organizaciones.png', 'documentos.png', 'relaciones.png'];
    const result = { status: errors.length ? 'page_errors' : 'verified',
      url: 'http://localhost:8501', screenshots, page_errors: errors };
    fs.writeFileSync(path.join(output, 'browser_verification.json'), JSON.stringify(result, null, 2) + '\n');
    if (errors.length) throw new Error('Se detectaron errores JavaScript en el navegador');
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  } finally {
    await browser.close();
  }
})().catch(error => { process.stderr.write(error.stack + '\n'); process.exitCode = 1; });
