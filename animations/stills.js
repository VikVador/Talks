// Stills of the recap videos: one image per step of each animation, taken at the end of each pause.
//   node animations/stills.js              -> every project of projects/
//   node animations/stills.js <project>
// An animation is a sequence of steps; each ends with a pause for the audience to read. Played from its HTML source,
// the canvas does not change from frame to frame during a pause, so a pause is a run of identical frames of at
// least MIN_PAUSE seconds. Its last frame is saved as projects/<project>/<video>/NN.jpg and listed under `stills`
// in project.yaml. The PDF of a deck shows these stills, one slide each, in place of the video (scripts/build.sh --pdf).
const fs = require('fs'), path = require('path'), yaml = require('js-yaml'), puppeteer = require('puppeteer-core');
const ROOT = path.join(__dirname, '..'), FPS = 10, MIN_PAUSE = 0.8, SAME_PX = 12;
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

async function stills(browser, source, outDir, samePx = SAME_PX) {
  const p = await browser.newPage();
  await p.setViewport({ width: 2000, height: 1300, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, `${source}.html`));
  await p.addStyleTag({ content: 'body{padding:0!important}.wrap{max-width:none!important;width:1920px!important;margin:0!important}.stage{width:1920px!important;height:1080px!important;border:0!important;border-radius:0!important}header,.controls,.hint{display:none!important}' });
  await p.evaluate(() => document.fonts.ready); await new Promise(r => setTimeout(r, 1500));
  await p.evaluate(() => window.dispatchEvent(new Event('resize'))); await new Promise(r => setTimeout(r, 500));
  const L = await p.evaluate(() => +document.querySelector('input[type=range]').max);
  const frame = tt => p.evaluate(tt => {           // draw story time tt, return the canvas in grey at 192 x 108
    playing = false; t = tt; draw(t);
    const c = document.querySelector('canvas'), s = document.createElement('canvas'); s.width = 192; s.height = 108;
    const x = s.getContext('2d'); x.drawImage(c, 0, 0, 192, 108);
    const d = x.getImageData(0, 0, 192, 108).data, g = [];
    for (let i = 0; i < d.length; i += 4) g.push((d[i] + d[i + 1] + d[i + 2]) / 3);
    return g;
  }, tt);
  // two frames are the same screen when at most samePx pixels differ by more than 2 levels: small looping details
  // (the "…" dots) keep moving during a pause; a video with larger ones sets `same_px` in project.yaml
  const same = (a, b) => a.reduce((n, v, i) => n + (Math.abs(v - b[i]) > 2), 0) <= samePx;
  const times = [], grey = [];
  for (let i = 0; i <= Math.round(L * FPS); i++) { times.push(Math.min(L, i / FPS)); grey.push(await frame(times[i])); }
  const ends = [];                                 // last time of each run of identical frames lasting >= MIN_PAUSE
  for (let i = 0, s = 0; i < grey.length; i++) {
    if (i === grey.length - 1 || !same(grey[i + 1], grey[i])) {
      if (times[i] - times[s] >= MIN_PAUSE - 1e-6 || i === grey.length - 1) ends.push(times[i]);
      s = i + 1;
    }
  }
  fs.rmSync(outDir, { recursive: true, force: true }); fs.mkdirSync(outDir, { recursive: true });
  const cv = await p.$('canvas'), names = [];
  for (const [k, tt] of ends.entries()) {
    await frame(tt);
    const name = `${String(k + 1).padStart(2, '0')}.jpg`;
    await cv.screenshot({ path: path.join(outDir, name), type: 'jpeg', quality: 88 });
    names.push(`${path.basename(outDir)}/${name}`);
  }
  await p.close();
  return names;
}

(async () => {
  const dirs = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(path.join(ROOT, 'projects'));
  const browser = await puppeteer.launch({ executablePath: CHROME, args: ['--disable-gpu'] });
  for (const d of dirs) {
    const file = path.join(ROOT, 'projects', d, 'project.yaml');
    if (!fs.existsSync(file)) continue;
    const text = fs.readFileSync(file, 'utf8'), project = yaml.load(text);
    for (const v of project.videos) v.stills = await stills(browser, v.source, path.join(ROOT, 'projects', d, v.file.replace(/\.mp4$/, '')), v.same_px);
    const head = text.split(/^videos:/m)[0];
    const body = 'videos:           # recap videos in order: file (poster: same name, .jpg), source in animations/, stills (animations/stills.js)\n' +
      project.videos.map(v => `  - file: ${v.file}\n    source: ${v.source}\n` + (v.same_px ? `    same_px: ${v.same_px}\n` : '') + `    stills:\n` + v.stills.map(s => `      - ${s}\n`).join('')).join('');
    fs.writeFileSync(file, head + body);
    console.log(d, project.videos.map(v => `${v.file}: ${v.stills.length}`).join(', '));
  }
  await browser.close();
})();
