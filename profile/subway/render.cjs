// node render.cjs "page.html?query" out.webp|out.png [seconds=6] [fps=24] [width=1200]
// Seek contract: every frame calls window.__seek(ms) if the page defines it, and pauses + seeks every CSS / WAAPI animation.
// The clock is seeked, never watched, so renders are deterministic. A .png output is the frame at 0 ms.
// Loops are encoded as animated WebP and stepped down in size until they are under MAX_MB (default 2.9).
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const [page_, out, secs = '6', fps = '24', w = '1200'] = process.argv.slice(2);
  const [file, query = ''] = page_.split('?');
  const url = 'file://' + path.resolve(file) + (query ? '?' + query : '');
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: +w, height: 800 }, deviceScaleFactor: 1.5 });
  const page = await ctx.newPage();
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => window.__ready || null);                    // pages may expose a promise (image preloads)
  const H = await page.evaluate(() => Math.ceil(document.querySelector('#stage').getBoundingClientRect().height));
  await page.setViewportSize({ width: +w, height: H });
  await page.waitForTimeout(300);
  const seek = t => page.evaluate(t => { window.__seek && window.__seek(t); for (const a of document.getAnimations()) { a.pause(); a.currentTime = t; } }, t);
  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
  if (out.endsWith('.png')) {
    await seek(+(process.env.STILL_MS || 0)); await page.screenshot({ path: out, omitBackground: true }); await browser.close();
    console.error(out, `${Math.round(+w * 1.5)}x${Math.round(H * 1.5)}`, (fs.statSync(out).size / 1e3 | 0) + ' KB'); return;
  }
  const tmp = fs.mkdtempSync(path.join(path.dirname(path.resolve(out)), '.frames-'));
  const n = Math.round(+secs * +fps);
  for (let i = 0; i < n; i++) { await seek(i / +fps * 1000); await page.screenshot({ path: path.join(tmp, `f_${String(i).padStart(4, '0')}.png`), omitBackground: true }); }
  await browser.close();
  try {
    execFileSync(process.env.PY || 'python3', ['-c', `
import sys, glob, os
from PIL import Image
tmp, out, fps, cap = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]) * 1e6
src = [Image.open(f).convert('RGBA') for f in sorted(glob.glob(tmp + '/f_*.png'))]
W0 = src[0].width
for scale, q in [(1, 78), (1, 70), (.9, 70), (.8, 68), (.72, 66), (.64, 62), (.56, 58)]:
    W = round(W0 * scale)
    ims = src if scale == 1 else [i.resize((W, round(i.height * W / i.width)), Image.LANCZOS) for i in src]
    ims[0].save(out, save_all=True, append_images=ims[1:], duration=round(1000 / fps), loop=0, quality=q, method=5)
    if os.path.getsize(out) <= cap: break
src[0].save(out.rsplit('.', 1)[0] + '.png')
print(out, len(ims), 'frames', ims[0].size, 'q%d' % q, '%.2f MB' % (os.path.getsize(out) / 1e6), file=sys.stderr)
`, tmp, out, fps, process.env.MAX_MB || '2.9'], { stdio: 'inherit' });
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
})();
