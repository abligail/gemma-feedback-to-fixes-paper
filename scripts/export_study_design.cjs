// Optional re-export of Figure 1. The default paper build verifies bundled exports.
// Install Playwright and its Chromium browser only when changing the SVG artwork.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [source, rawPdf, png] = process.argv.slice(2);
  if (!source || !rawPdf || !png) throw new Error('Expected SVG, raw PDF, and PNG paths.');
  const bytes = fs.readFileSync(source, 'utf8');
  const svg = bytes.slice(bytes.indexOf('<svg'));
  if (!svg.startsWith('<svg')) throw new Error('Missing SVG root.');
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({
      viewport: { width: 1536, height: 1024 }, deviceScaleFactor: 2,
    });
    const page = await context.newPage();
    await page.setContent(`<!doctype html><html><head><style>
      @page { size:1536px 1024px; margin:0; }
      html,body { width:1536px; height:1024px; margin:0; padding:0; overflow:hidden; background:white; }
      svg { display:block; width:1536px; height:1024px; }
      * { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
    </style></head><body>${svg}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    for (const file of [rawPdf, png]) fs.mkdirSync(path.dirname(file), { recursive: true });
    await page.screenshot({ path: png, type: 'png', clip: { x: 0, y: 0, width: 1536, height: 1024 } });
    await page.pdf({
      path: rawPdf, width: '1536px', height: '1024px', preferCSSPageSize: true,
      printBackground: true, displayHeaderFooter: false,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
    });
    console.log(JSON.stringify({ browser: browser.version(), png_pixels: [3072, 2048] }));
    await context.close();
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
