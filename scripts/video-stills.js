// For the PDF: replace every recap video slide of a deck by one slide per still of the video (projects/*/project.yaml,
// made by animations/stills.js). The first keeps the page number, the next ones hold it (`_paginate: hold`), so the
// stills of one video share its page number and are browsed with the arrows.
//   node scripts/video-stills.js <deck.md> <out.md>
const fs = require('fs'), path = require('path'), yaml = require('js-yaml');
const [src, out] = process.argv.slice(2), dir = path.dirname(path.resolve(src));
const md = fs.readFileSync(src, 'utf8');
const parts = md.split(/\n---\n/);                 // parts[0] is the front matter
const result = parts.map((slide, i) => {
  const m = i > 0 && slide.match(/<video class="full" src="([^"]+)"[^>]*><\/video>/);
  if (!m) return slide;
  const video = path.resolve(dir, m[1]), project = path.join(path.dirname(video), 'project.yaml');
  const entry = fs.existsSync(project) && (yaml.load(fs.readFileSync(project, 'utf8')).videos || [])
    .find(v => v.file === path.basename(video));
  if (!entry || !entry.stills || !entry.stills.length) return slide;
  return entry.stills.map((s, k) => {
    const rel = path.relative(dir, path.join(path.dirname(video), s)).split(path.sep).join('/');
    let one = slide.replace(m[0], `<img class="full" src="${rel}">`);
    if (k > 0) one = one.replace(/<!--\s*RULE[\s\S]*?-->\n*/g, '').replace(/^(\s*<!-- _class: video -->)/m, '$1\n<!-- _paginate: hold -->');
    return one;
  }).join('\n---\n');
});
fs.writeFileSync(out, result.join('\n---\n'));
