// Recap videos (video.full on slides with class `video`):
// - restart when their slide is entered, pause when it is left;
// - play/pause button bottom-left (a click on the video toggles too);
// - a seek bar that appears when the mouse is over the button area: click or drag to jump.
// Arrow keys keep changing slides after a click (focus is never kept on the controls).
// Injected into every built deck by scripts/build.sh; styles are in theme/base.css (.vdock, .vctl, .vbar).
(function () {
  const ICON_PAUSE = '<svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>';
  const ICON_PLAY  = '<svg viewBox="0 0 24 24"><path d="M8 5.5v13a1 1 0 0 0 1.5.9l10.2-6.5a1 1 0 0 0 0-1.7L9.5 4.6A1 1 0 0 0 8 5.5z"/></svg>';
  const fmt = x => { x = Math.max(0, Math.floor(x || 0)); return Math.floor(x / 60) + ':' + String(x % 60).padStart(2, '0'); };

  function init() {
    const videos = [...document.querySelectorAll('section video.full')];
    videos.forEach(v => {
      const dock = document.createElement('div'); dock.className = 'vdock';
      const btn = document.createElement('button');
      btn.className = 'vctl'; btn.type = 'button'; btn.setAttribute('aria-label', 'Play or pause the animation');
      const bar = document.createElement('div'); bar.className = 'vbar';
      bar.innerHTML = '<div class="track"><div class="fill"></div><div class="knob"></div></div><span class="time">0:00</span>';
      const track = bar.querySelector('.track'), fill = bar.querySelector('.fill'),
            knob = bar.querySelector('.knob'), time = bar.querySelector('.time');

      const paint = () => { btn.innerHTML = v.paused ? ICON_PLAY : ICON_PAUSE; };
      const toggle = e => { e.stopPropagation(); e.preventDefault(); v.paused ? v.play().catch(() => {}) : v.pause(); btn.blur(); };
      const draw = () => {
        const f = v.duration ? v.currentTime / v.duration : 0;
        fill.style.width = knob.style.left = (100 * f) + '%';
        time.textContent = fmt(v.currentTime) + ' / ' + fmt(v.duration);
      };
      const loop = () => { draw(); if (!v.paused) requestAnimationFrame(loop); };
      // The slide may be scaled: use the track's on-screen box.
      const seek = e => {
        const r = track.getBoundingClientRect();
        const f = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width));
        if (v.duration) v.currentTime = f * v.duration;
        draw();
      };
      bar.addEventListener('mousedown', e => {
        e.preventDefault(); e.stopPropagation(); dock.classList.add('drag'); seek(e);
        const mv = ev => seek(ev);
        const up = () => { dock.classList.remove('drag'); removeEventListener('mousemove', mv); removeEventListener('mouseup', up); };
        addEventListener('mousemove', mv); addEventListener('mouseup', up);
      });
      bar.addEventListener('click', e => e.stopPropagation());
      btn.addEventListener('mousedown', e => e.preventDefault());
      btn.addEventListener('click', toggle);
      v.addEventListener('click', toggle);
      v.addEventListener('play', () => { paint(); loop(); });
      v.addEventListener('pause', () => { paint(); draw(); });
      v.addEventListener('seeked', draw);
      v.addEventListener('loadedmetadata', draw);
      paint();
      dock.append(btn, bar);
      v.parentNode.appendChild(dock);
    });

    // Restart a video when its slide becomes active, pause it when the slide is left.
    const sync = () => videos.forEach(v => {
      const host = v.closest('svg[data-marpit-svg]') || v.closest('section');
      const active = !!(host && host.closest('.bespoke-marp-active'));
      if (active && !v._active) { v.currentTime = 0; v.play().catch(() => {}); }
      if (!active && v._active) v.pause();
      v._active = active;
    });
    new MutationObserver(sync).observe(document.body, { subtree: true, attributes: true, attributeFilter: ['class'] });
    sync();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
