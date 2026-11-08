// Render one animation to a 4K MP4: seek each frame, screenshot the canvas (PNG, lossless), pipe to ffmpeg.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const [name, fps] = process.argv.slice(2);
(async () => {
  const out = require('path').join(__dirname, 'out', `${name}.mp4`);
  require('fs').mkdirSync(require('path').dirname(out), { recursive: true });
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-threads', '2', '-preset', 'medium', '-crf', '20', '-tune', 'animation', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
  ff.stderr.on('data', d => process.stderr.write(d));
  const done = new Promise(r => ff.on('close', r));
  const b = await chromium.launch({ args: ['--disable-dev-shm-usage', '--disable-gpu'] }); const p = await b.newPage({ viewport: { width: 2000, height: 1300 }, deviceScaleFactor: 2 });
  await p.goto('file://' + require('path').join(__dirname, `${name}.html`));
  await p.addStyleTag({ content: 'body{padding:0!important}.wrap{max-width:none!important;width:1920px!important;margin:0!important}.stage{width:1920px!important;height:1080px!important;border:0!important;border-radius:0!important}header,.controls,.hint{display:none!important}' });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1500);
  await p.evaluate(() => window.dispatchEvent(new Event('resize'))); await p.waitForTimeout(500);
  const L = await p.evaluate(() => +document.querySelector('input[type=range]').max);
  const N = Math.round(L * fps) + Math.round(fps * 1.5);   // hold the last frame 1.5 s
  const cv = await p.$('canvas');
  for (let i = 0; i < N; i++) {
    await p.evaluate(tt => { playing = false; t = tt; draw(t); }, Math.min(L, i / fps));
    const buf = await cv.screenshot({ type: 'png' });
    if (i % 150 === 0) console.log(name, i, '/', N);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await done; await b.close();
  console.log(name, 'duration', L, 'frames', N);
})();
