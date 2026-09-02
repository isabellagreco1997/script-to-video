// Screenshot web pages for use as shots. node capture.js jobs.json
// jobs.json: [{"name":"wiki_door","url":"https://...","w":1600,"h":1000,"scroll":"h2#History","out":"assets/wiki_door.png","full":false}]
const puppeteer = require('puppeteer-core');
const fs = require('fs'), path = require('path');
const CHROME = process.env.CHROME || (process.platform === 'darwin' ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  : process.platform === 'win32' ? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' : '/usr/bin/google-chrome');
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--window-size=1700,1100', '--mute-audio'] });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36');
  for (const j of jobs) {
    try {
      await page.setViewport({ width: j.w || 1600, height: j.h || 1000, deviceScaleFactor: 1 });
      await page.goto(j.url, { waitUntil: 'networkidle2', timeout: 60000 });
      await sleep(1200);
      // dismiss common cookie banners
      await page.evaluate(() => { for (const b of document.querySelectorAll('button')) { const t = (b.textContent || '').toLowerCase(); if (/accept|agree|got it|reject all/.test(t)) { try { b.click(); } catch (e) {} } } });
      if (j.scroll) { await page.evaluate(sel => { const el = document.querySelector(sel); if (el) { el.scrollIntoView(); window.scrollBy(0, -40); } }, j.scroll); await sleep(600); }
      if (j.hide) { await page.addStyleTag({ content: j.hide + '{display:none!important}' }); }
      fs.mkdirSync(path.dirname(j.out), { recursive: true });
      await page.screenshot({ path: j.out, fullPage: !!j.full });
      console.log('shot', j.name);
    } catch (e) { console.log('FAILED', j.name, e.message); }
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
