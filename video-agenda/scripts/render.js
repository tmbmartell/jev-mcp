// Uso: node render.js <versao 1|2> <pasta_saida> [tempos de preview separados por vírgula]
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [v = '1', out = 'frames', only] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const url = 'file://' + path.resolve(__dirname, '../index.html') + `?v=${v}&capture=1`;
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  fs.writeFileSync(path.join(out, 'events.json'), JSON.stringify(await page.evaluate(() => window.__events())));
  const times = only ? only.split(',').map(Number) : [...Array(900).keys()].map(f => f / 30);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate(t => window.__render(t), times[i]);
    const name = only ? `t${times[i].toFixed(2)}.jpg` : `f${String(i).padStart(4, '0')}.jpg`;
    await page.screenshot({ path: path.join(out, name), type: 'jpeg', quality: 92 });
  }
  await browser.close();
})();
