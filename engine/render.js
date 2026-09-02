// Deterministic frame renderer: seeks the stage to each frame time and screenshots it via CDP.
// env: PORT (http server serving the work dir), OUT (frames dir), START_F/END_F (partial), CHROME (path)
const puppeteer = require('puppeteer-core');
const fs = require('fs'), path = require('path');
const FPS = 30;
const OUT = process.env.OUT || path.resolve(process.cwd(), 'render_frames');
fs.mkdirSync(OUT, { recursive: true });
const CHROME = process.env.CHROME || (process.platform === 'darwin' ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  : process.platform === 'win32' ? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' : '/usr/bin/google-chrome');
(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true,
    args: ['--window-size=2200,2200', '--autoplay-policy=no-user-gesture-required', '--hide-scrollbars', '--mute-audio', '--disable-gpu'] });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:' + (process.env.PORT || 8722) + '/stage.html', { waitUntil: 'networkidle2', timeout: 60000 });
  await page.waitForSelector('[data-om-exportable-video-with-duration-secs]', { timeout: 60000 });
  const meta = await page.evaluate(() => window.META);
  await page.setViewport({ width: meta.w, height: meta.h, deviceScaleFactor: 1 });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction('window.gifsReady === true', { timeout: 300000 });
  await new Promise(r => setTimeout(r, 1500));
  const N = Math.ceil(meta.dur * FPS);
  const cdp = await page.target().createCDPSession();
  const clip = { x: 0, y: 0, width: meta.w, height: meta.h, scale: 1 };
  const I0 = parseInt(process.env.START_F || '0'), I1 = Math.min(N, parseInt(process.env.END_F || String(N)));
  const t0 = Date.now();
  for (let i = I0; i < I1; i++) {
    const t = Math.min(i / FPS, meta.dur - 0.001);
    await page.evaluate(t => { const el = document.querySelector('[data-om-exportable-video-with-duration-secs]');
      el.dispatchEvent(new CustomEvent('data-om-seek-to-time-frame', { detail: { time: t, sync: true } })); }, t);
    const shot = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 90, clip, captureBeyondViewport: false });
    fs.writeFileSync(path.join(OUT, `f${String(i).padStart(5, '0')}.jpg`), Buffer.from(shot.data, 'base64'));
    if (i % 500 === 0) console.log(`${i}/${N} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  console.log('FRAMES DONE', I1 - I0, 'of', N);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
