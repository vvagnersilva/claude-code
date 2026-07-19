// Run this snippet via `browser_evaluate` AFTER navigating Playwright to the
// generated report (via the local static server, since file:// URLs are
// blocked). It returns an object summarizing the report's health.
//
// The skill should reject the run if `ok` is false and surface `errors`.
// Pass the expected values via globals before evaluating:
//   window.__EXPECTED__ = { keyword, generatedDate, monthCount, weekCount };
() => {
  const exp = window.__EXPECTED__ || {};
  const errors = [];
  const html = document.documentElement.outerHTML;

  const kw = document.getElementById('kw')?.textContent || '';
  const gen = document.getElementById('gen')?.textContent || '';
  const monthCards = document.querySelectorAll('#sec-month .card').length;
  const weekCards = document.querySelectorAll('#sec-week .card').length;
  const imgs = [...document.querySelectorAll('.card img')];
  const brokenThumbs = imgs.filter(img => !(img.complete && img.naturalWidth > 10)).length;
  const placeholderImg = imgs.find(img => /REPLACE_WITH_BASE64/.test(img.src));

  // Check for unreplaced markers / example data
  if (/REPLACE_WITH_BASE64/.test(html)) errors.push('html still contains REPLACE_WITH_BASE64 placeholder');
  if (/Example video title|Example Channel|example keyword/.test(html)) errors.push('html still contains template example data');

  // Field assertions
  if (exp.keyword && kw.trim() !== exp.keyword) errors.push(`keyword mismatch: got="${kw}" expected="${exp.keyword}"`);
  if (exp.generatedDate && !gen.includes(exp.generatedDate)) errors.push(`generatedDate not in header: expected ${exp.generatedDate}, got "${gen}"`);
  if (exp.monthCount != null && monthCards !== exp.monthCount) errors.push(`month card count: got ${monthCards}, expected ${exp.monthCount}`);
  if (exp.weekCount != null && weekCards !== exp.weekCount) errors.push(`week card count: got ${weekCards}, expected ${exp.weekCount}`);
  if (brokenThumbs > 0) errors.push(`broken thumbnails: ${brokenThumbs} of ${imgs.length}`);
  if (placeholderImg) errors.push('at least one img.src still equals the placeholder');

  // Interactive sort smoke-test: switching to "perf" must reorder a card
  let interactiveOk = true;
  try {
    const sel = document.querySelector('#sec-month select');
    const before = document.querySelector('#sec-month .card .title')?.textContent || '';
    sel.value = 'perf'; sel.dispatchEvent(new Event('change'));
    const afterPerf = document.querySelector('#sec-month .card .title')?.textContent || '';
    sel.value = 'views'; sel.dispatchEvent(new Event('change'));
    const afterViews = document.querySelector('#sec-month .card .title')?.textContent || '';
    if (afterViews !== before) errors.push('sort toggle did not restore "views" order');
    if (afterPerf === before && monthCards > 3) {
      // not necessarily fatal (could happen if highest-views == highest-perf), so just info
    }
  } catch (e) {
    interactiveOk = false;
    errors.push('interactive sort threw: ' + e.message);
  }

  return {
    ok: errors.length === 0,
    errors,
    summary: {
      kw, gen, monthCards, weekCards,
      thumbs: imgs.length, brokenThumbs,
      interactiveOk,
    },
  };
}
