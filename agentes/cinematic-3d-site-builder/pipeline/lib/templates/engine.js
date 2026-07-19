/* ============================================================================
 * engine.js — the continuity / 3D-scroll engine (webgl mode).
 * A pure function of window.__STORY__ (emitted by the PLAN stage).
 * Globals expected: THREE (r149 UMD), gsap, ScrollTrigger, Lenis.
 * See docs/logic.md for the full explanation.
 * ==========================================================================*/
(function () {
  'use strict';
  const STORY = window.__STORY__;
  const canvas = document.getElementById('scene');
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── renderer / scene / camera ──────────────────────────────────────────────
  // preserveDrawingBuffer lets QC sample the rendered pixels via drawImage()
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  const bg = new THREE.Color(STORY.bg);
  scene.background = bg.clone();
  scene.fog = new THREE.FogExp2(bg.clone(), STORY.archetype === 'orbit' ? 0.010 : 0.016);

  const camera = new THREE.PerspectiveCamera(58, window.innerWidth / window.innerHeight, 0.1, 3000);

  // ── build the camera path from waypoints ───────────────────────────────────
  const SCALE = 1.0;
  const wps = STORY.waypoints;
  const pts = wps.map((w) => new THREE.Vector3(w.pos[0] * SCALE, w.pos[1] * SCALE, w.pos[2] * SCALE));
  if (pts.length < 2) pts.push(pts[0].clone().add(new THREE.Vector3(0, -40, -40)));
  const isOrbit = STORY.camera.path === 'orbit';
  const curve = new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0.5);

  // waypoint colors for the continuous color-grade
  const fogColors = wps.map((w) => new THREE.Color(w.fog));
  const parColors = wps.map((w) => new THREE.Color(w.particle.color));
  function gradeAt(p, arr) {
    const n = arr.length; if (n === 1) return arr[0].clone();
    const f = p * (n - 1); const i = Math.min(n - 2, Math.floor(f)); const t = f - i;
    return arr[i].clone().lerp(arr[i + 1], t);
  }

  // ── lights ─────────────────────────────────────────────────────────────────
  const accent = new THREE.Color(STORY.accent);
  scene.add(new THREE.AmbientLight(0xffffff, 0.25));
  const keyLight = new THREE.DirectionalLight(0xbcd8ff, 0.8);
  keyLight.position.set(10, 40, 20); scene.add(keyLight);
  const accentLight = new THREE.PointLight(accent.getHex(), 1.2, 220, 2); scene.add(accentLight);

  // ── the hero subject (procedural stand-in for the Seedance hero clip) ───────
  const subject = buildSubject(STORY.subject || 'faceted-solid', accent);
  scene.add(subject.group);

  // floodlights that ignite in the dark zones (descent). Off by default.
  const flood = new THREE.SpotLight(accent.getHex(), 0, 260, Math.PI / 6, 0.4, 1.2);
  flood.position.set(0, 6, 0); subject.group.add(flood);
  const floodTarget = new THREE.Object3D(); floodTarget.position.set(0, -30, 0);
  subject.group.add(floodTarget); flood.target = floodTarget;

  // ── particle fields (world-static → fly past as camera moves = motion) ──────
  const field = buildField(pts, isOrbit ? 44 : 70, isOrbit ? 900 : 2200, accent);
  scene.add(field.points);
  const nearField = buildNearField(1200, accent); scene.add(nearField.points);

  // ── god rays near the top (descent) + vent glow near the floor ──────────────
  const godrays = (STORY.archetype === 'descent') ? buildGodRays(pts[0]) : null;
  if (godrays) scene.add(godrays);
  const vents = (STORY.archetype === 'descent') ? buildVents(pts[pts.length - 1], accent) : null;
  if (vents) scene.add(vents);

  // drifting "creatures" — a few emissive bodies scattered along the path
  const creatures = buildCreatures(pts, accent, STORY.archetype);
  creatures.forEach((c) => scene.add(c.mesh));

  // ── scroll wiring: Lenis smooth scroll + GSAP ScrollTrigger ─────────────────
  gsap.registerPlugin(ScrollTrigger);
  let progress = 0;
  const lenis = new Lenis({ lerp: 0.09, wheelMultiplier: 1, smoothWheel: true });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);

  function computeProgress() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
  }

  // section reveals + HUD driven by ScrollTrigger
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
  document.querySelectorAll('.chapter').forEach((el) => {
    gsap.fromTo(el.querySelector('.chapter-inner'),
      { autoAlpha: 0, y: 48 },
      { autoAlpha: 1, y: 0, ease: 'power2.out', duration: 1,
        scrollTrigger: { trigger: el, start: 'top 78%', end: 'bottom 40%', toggleActions: 'play reverse play reverse' } });
  });

  // ── resize ─────────────────────────────────────────────────────────────────
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // ── main loop ──────────────────────────────────────────────────────────────
  const tmpA = new THREE.Vector3(), tmpB = new THREE.Vector3();
  let clock = 0;
  function frame(dt) {
    clock += dt;
    computeProgress();
    const p = progress;

    // camera along the path (or orbiting the subject)
    if (isOrbit) {
      const R = STORY.camera.radius || 46;
      const a = p * Math.PI * 2;
      camera.position.set(Math.cos(a) * R, Math.sin(p * Math.PI * 2) * 6 + 3, Math.sin(a) * R);
      camera.lookAt(0, 0, 0);
      subject.group.rotation.y = a * 0.6 + clock * 0.05;
    } else {
      curve.getPointAt(p, tmpA);
      camera.position.copy(tmpA);
      const ahead = Math.min(1, p + (STORY.camera.lookAhead || 0.05));
      curve.getPointAt(ahead, tmpB);
      // subject leads the camera down the path so it's always in view + descending
      subject.group.position.lerp(tmpB, 0.15);
      subject.group.position.y -= 6; subject.group.position.z -= 2;
      camera.lookAt(subject.group.position);
      subject.group.rotation.y += dt * 0.15;
      subject.group.position.x += Math.sin(clock * 0.6) * 0.02; // gentle bob
      subject.group.position.y += Math.sin(clock * 0.9) * 0.03;
    }

    // continuous color-grade → the seamless morph between sections
    const fog = gradeAt(p, fogColors);
    scene.fog.color.copy(fog);
    scene.background.copy(fog);
    const par = gradeAt(p, parColors);
    field.points.material.color.copy(par);
    nearField.points.material.color.copy(par);
    accentLight.position.copy(camera.position).add(new THREE.Vector3(6, 4, 6));

    // near field follows the camera for constant local density
    nearField.points.position.copy(camera.position);
    nearField.points.rotation.y = clock * 0.02;

    // floodlights ignite in the dark half (descent) — the hero→section transform
    const wantFlood = STORY.archetype === 'descent' && p >= 0.45;
    flood.intensity += ((wantFlood ? 3.2 : 0) - flood.intensity) * Math.min(1, dt * 2);
    subject.viewport && (subject.viewport.material.emissiveIntensity = 0.6 + Math.sin(clock * 2) * 0.25);

    // god rays fade with depth; vents glow near the floor
    if (godrays) godrays.material.opacity = 0.35 * Math.max(0, 1 - p * 2.2);
    if (vents) vents.children.forEach((m, i) => { m.material.emissiveIntensity = Math.max(0, (p - 0.8) * 5) * (0.6 + 0.4 * Math.sin(clock * 3 + i)); });

    // creatures pulse
    creatures.forEach((c, i) => {
      c.mesh.material.emissiveIntensity = 0.4 + 0.4 * Math.sin(clock * 2 + i);
      c.mesh.position.x = c.base.x + Math.sin(clock * 0.5 + i) * 2;
      c.mesh.rotation.y += dt * 0.3;
    });

    field.points.rotation.y = clock * 0.006;

    // HUD
    if (hudValue && STORY.hud) {
      const v = Math.round(hudAt(p));
      hudValue.textContent = v.toLocaleString() + (STORY.hud.unit ? ' ' + STORY.hud.unit : '');
    }
    if (hudBar) hudBar.style.transform = `scaleY(${p})`;

    renderer.render(scene, camera);
    window.__RENDERED__ = (window.__RENDERED__ || 0) + 1;
    window.__PROGRESS__ = p;
  }

  let last = performance.now();
  function loop(now) {
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    frame(reduce ? 0.0001 : dt);
    requestAnimationFrame(loop);
  }
  // expose for verify: force a scroll + render at an arbitrary fraction
  window.__scrollTo = (frac) => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    window.scrollTo(0, max * frac);
    lenis.scrollTo(max * frac, { immediate: true });
  };
  requestAnimationFrame(loop);
  window.__ENGINE_READY__ = true;

  /* ---- builders --------------------------------------------------------- */
  function buildSubject(kind, col) {
    const g = new THREE.Group();
    const metal = new THREE.MeshStandardMaterial({ color: 0x11161f, metalness: 0.85, roughness: 0.35 });
    let viewport = null;
    if (kind === 'submarine') {
      const hull = new THREE.Mesh(new THREE.CapsuleGeometry(3.4, 11, 8, 20), metal);
      hull.rotation.z = Math.PI / 2; g.add(hull);
      const tower = new THREE.Mesh(new THREE.BoxGeometry(3, 3.4, 3.2), metal); tower.position.set(-1, 3.2, 0); g.add(tower);
      const ring = new THREE.Mesh(new THREE.TorusGeometry(1.7, 0.35, 12, 28),
        new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 0.8, metalness: 0.4, roughness: 0.3 }));
      ring.position.set(7, 0, 0); ring.rotation.y = Math.PI / 2; g.add(ring); viewport = ring;
      const fin = new THREE.Mesh(new THREE.ConeGeometry(2, 5, 4), metal); fin.rotation.z = -Math.PI / 2; fin.position.set(-8.5, 0, 0); g.add(fin);
    } else if (kind === 'hypercar') {
      const body = new THREE.Mesh(new THREE.BoxGeometry(14, 2.4, 5), new THREE.MeshStandardMaterial({ color: 0x0a0a0a, metalness: 0.9, roughness: 0.25 }));
      g.add(body);
      const cabin = new THREE.Mesh(new THREE.BoxGeometry(6, 2, 4.4), metal); cabin.position.set(-0.5, 1.8, 0); g.add(cabin);
      const bar = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.5, 5), new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 1 }));
      bar.position.set(7, 0.3, 0); g.add(bar); viewport = bar;
      [-4.5, 4.5].forEach((x) => [-2.6, 2.6].forEach((z) => { const w = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 1, 18), metal); w.rotation.x = Math.PI / 2; w.position.set(x, -1.1, z); g.add(w); }));
    } else if (kind === 'tower') {
      const t = new THREE.Mesh(new THREE.BoxGeometry(8, 46, 8), new THREE.MeshStandardMaterial({ color: 0x0b0b12, metalness: 0.6, roughness: 0.2, emissive: col, emissiveIntensity: 0.05 }));
      g.add(t); viewport = t;
    } else if (kind === 'figure') {
      const head = new THREE.Mesh(new THREE.SphereGeometry(2.2, 24, 24), metal); head.position.y = 7; g.add(head);
      const torso = new THREE.Mesh(new THREE.CapsuleGeometry(2.4, 6, 6, 16), metal); torso.position.y = 1.5; g.add(torso);
      viewport = head;
    } else { // faceted-solid (luxury product)
      const solid = new THREE.Mesh(new THREE.IcosahedronGeometry(6, 0),
        new THREE.MeshStandardMaterial({ color: 0x0c0c0c, metalness: 1, roughness: 0.18, emissive: col, emissiveIntensity: 0.12, flatShading: true }));
      g.add(solid);
      const halo = new THREE.Mesh(new THREE.TorusGeometry(9, 0.14, 10, 60), new THREE.MeshBasicMaterial({ color: col }));
      halo.rotation.x = Math.PI / 2.3; g.add(halo); viewport = solid;
    }
    return { group: g, viewport };
  }

  function buildField(pathPts, spread, count, col) {
    const geo = new THREE.BufferGeometry();
    const arr = new Float32Array(count * 3);
    const yMin = Math.min(...pathPts.map((v) => v.y)) - 30;
    const yMax = Math.max(...pathPts.map((v) => v.y)) + 30;
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * spread * 2;
      arr[i * 3 + 1] = yMin + Math.random() * (yMax - yMin);
      arr[i * 3 + 2] = (Math.random() - 0.5) * spread * 2;
    }
    geo.setAttribute('position', new THREE.BufferAttribute(arr, 3));
    const mat = new THREE.PointsMaterial({ color: col, size: 0.5, transparent: true, opacity: 0.7, depthWrite: false, sizeAttenuation: true });
    return { points: new THREE.Points(geo, mat) };
  }
  function buildNearField(count, col) {
    const geo = new THREE.BufferGeometry();
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) { arr[i * 3] = (Math.random() - 0.5) * 90; arr[i * 3 + 1] = (Math.random() - 0.5) * 90; arr[i * 3 + 2] = (Math.random() - 0.5) * 90; }
    geo.setAttribute('position', new THREE.BufferAttribute(arr, 3));
    const mat = new THREE.PointsMaterial({ color: col, size: 0.32, transparent: true, opacity: 0.5, depthWrite: false });
    return { points: new THREE.Points(geo, mat) };
  }
  function buildGodRays(top) {
    const g = new THREE.Group();
    const mat = new THREE.MeshBasicMaterial({ color: 0xbfe0ff, transparent: true, opacity: 0.3, depthWrite: false, blending: THREE.AdditiveBlending });
    for (let i = 0; i < 6; i++) {
      const cone = new THREE.Mesh(new THREE.ConeGeometry(6 + i * 2, 90, 12, 1, true), mat.clone());
      cone.position.set((Math.random() - 0.5) * 40, top.y + 30, (Math.random() - 0.5) * 40);
      cone.rotation.x = Math.PI; g.add(cone);
    }
    g.material = mat; g.children.forEach(c => c.material = mat); return g;
  }
  function buildVents(bottom, col) {
    const g = new THREE.Group();
    for (let i = 0; i < 5; i++) {
      const m = new THREE.Mesh(new THREE.ConeGeometry(2 + Math.random() * 2, 8, 10),
        new THREE.MeshStandardMaterial({ color: 0x1a0e08, emissive: col, emissiveIntensity: 0 }));
      m.position.set((Math.random() - 0.5) * 60, bottom.y - 6 + Math.random() * 3, (Math.random() - 0.5) * 60);
      g.add(m);
    }
    return g;
  }
  function buildCreatures(pathPts, col, arche) {
    const list = []; const n = 10;
    const yMin = Math.min(...pathPts.map((v) => v.y)); const yMax = Math.max(...pathPts.map((v) => v.y));
    for (let i = 0; i < n; i++) {
      const mesh = new THREE.Mesh(new THREE.IcosahedronGeometry(0.7 + Math.random(), 0),
        new THREE.MeshStandardMaterial({ color: 0x0a0a0a, emissive: col, emissiveIntensity: 0.5, transparent: true, opacity: 0.9 }));
      const base = new THREE.Vector3((Math.random() - 0.5) * 60, yMin + Math.random() * (yMax - yMin), (Math.random() - 0.5) * 60 - 10);
      mesh.position.copy(base); list.push({ mesh, base });
    }
    return list;
  }
})();
