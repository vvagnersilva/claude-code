/* ============================================================================
 * frameseq.js — the EXACT PDF technique: a canvas frame-sequence scrubber.
 * "this scrolling effect ... is technically a video separated into multiple
 *  frames" [VIDEO]. Scroll progress → frame index → drawImage on a canvas.
 * Consumes the frames written by the ASSETS stage (real Seedance decode, or
 * procedural SVG placeholders). window.__STORY__.frames describes them.
 * ==========================================================================*/
(function () {
  'use strict';
  const STORY = window.__STORY__;
  const canvas = document.getElementById('scene');
  const ctx = canvas.getContext('2d');
  const F = STORY.frames || { count: 48, dir: 'assets/frames', pattern: 'frame-%03d.svg' };
  const pad = (F.pattern.match(/%0(\d+)/) || [, '3'])[1] | 0;
  const ext = F.pattern.split('.').pop();

  function pathFor(i) {
    return `${F.dir}/frame-${String(i).padStart(pad, '0')}.${ext}`;
  }

  // preload all frames
  const imgs = [];
  let loaded = 0;
  for (let i = 0; i < F.count; i++) {
    const im = new Image();
    im.onload = () => { loaded++; if (loaded === 1) resize(); };
    im.src = pathFor(i);
    imgs.push(im);
  }

  function resize() {
    canvas.width = window.innerWidth * Math.min(window.devicePixelRatio || 1, 2);
    canvas.height = window.innerHeight * Math.min(window.devicePixelRatio || 1, 2);
    // Resizing resets 2d-context state — re-enable high-quality resampling so
    // the cover-fit upscale doesn't pixelate on Retina backing stores.
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';
  }
  window.addEventListener('resize', resize); resize();

  let progress = 0;
  const lenis = new Lenis({ lerp: 0.09, smoothWheel: true });
  gsap.registerPlugin(ScrollTrigger);
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((t) => lenis.raf(t * 1000)); gsap.ticker.lagSmoothing(0);
  document.querySelectorAll('.chapter').forEach((el) => {
    gsap.fromTo(el.querySelector('.chapter-inner'), { autoAlpha: 0, y: 48 }, { autoAlpha: 1, y: 0, duration: 1,
      scrollTrigger: { trigger: el, start: 'top 78%', end: 'bottom 40%', toggleActions: 'play reverse play reverse' } });
  });

  const hudValue = document.getElementById('hud-value');
  const hudBar = document.getElementById('hud-bar');
  // HUD value: piecewise-linear between the sections' hudValues (supports
  // non-linear and non-monotonic counters, e.g. parts 1 → 847 → 1). Falls back
  // to a global from→to lerp when sections carry no usable values.
  const hudStops = (STORY.sections || []).filter((s) => typeof s.hudValue === 'number');
  function hudAt(pr) {
    if (hudStops.length < 2) return STORY.hud.from + (STORY.hud.to - STORY.hud.from) * pr;
    let a = hudStops[0], b = hudStops[hudStops.length - 1];
    for (let i = 0; i < hudStops.length - 1; i++) {
      if (pr >= hudStops[i].start && pr <= hudStops[i + 1].start) { a = hudStops[i]; b = hudStops[i + 1]; break; }
    }
    const t = Math.min(1, Math.max(0, (pr - a.start) / ((b.start - a.start) || 1)));
    return a.hudValue + (b.hudValue - a.hudValue) * t;
  }
  function draw() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    const idx = Math.round(progress * (F.count - 1));
    const im = imgs[idx];
    if (im && im.complete && im.naturalWidth) {
      // cover-fit
      const cw = canvas.width, ch = canvas.height, iw = im.naturalWidth, ih = im.naturalHeight;
      const s = Math.max(cw / iw, ch / ih);
      const w = iw * s, h = ih * s;
      ctx.drawImage(im, (cw - w) / 2, (ch - h) / 2, w, h);
    }
    if (hudValue && STORY.hud) {
      const v = Math.round(hudAt(progress));
      hudValue.textContent = v.toLocaleString() + (STORY.hud.unit ? ' ' + STORY.hud.unit : '');
    }
    if (hudBar) hudBar.style.transform = `scaleY(${progress})`;
    window.__RENDERED__ = (window.__RENDERED__ || 0) + 1;
    window.__PROGRESS__ = progress;
    requestAnimationFrame(draw);
  }
  window.__scrollTo = (frac) => { const max = document.documentElement.scrollHeight - window.innerHeight; window.scrollTo(0, max * frac); lenis.scrollTo(max * frac, { immediate: true }); };
  requestAnimationFrame(draw);
  window.__ENGINE_READY__ = true;
})();
