// Paste this function into `browser_evaluate` on a channel's /videos page.
// Returns the viewsText of up to the 12 most recent REGULAR videos,
// skipping Shorts and live streams.
//
// IMPORTANT: This selector set works against YouTube's current
// `yt-lockup-view-model` layout (Q1 2026). Older snippets that relied solely
// on `.inline-metadata-item` and `#metadata-line span` started returning empty
// arrays for some channels — see the project memory.
async () => {
  window.scrollBy(0, 1500);
  await new Promise(r => setTimeout(r, 1000));
  const items = [...document.querySelectorAll(
    'ytd-rich-item-renderer, ytd-grid-video-renderer')];
  const out = [];
  for (const it of items) {
    if (out.length >= 12) break;
    // skip Shorts
    const link = it.querySelector('a[href*="/shorts/"], a[href*="/watch?"]');
    if (link && /\/shorts\//.test(link.getAttribute('href') || '')) continue;
    // skip live / upcoming / streamed (multi-language)
    const liveBadge = [...it.querySelectorAll(
      '.badge-shape-wiz__text, .yt-badge-shape__text')]
      .map(e => e.textContent.trim().toUpperCase())
      .find(t => /LIVE|AO VIVO|EN VIVO|EN DIRECTO|STREAMED|WATCHING|PREMIER|UPCOMING|AGENDADO|首播|直播/.test(t));
    if (liveBadge) continue;

    // Find first text that looks like a view count. Require the string to
    // START with a number so we don't grab a video title that contains "view".
    const allText = [...it.querySelectorAll(
      'span, yt-formatted-string, .yt-content-metadata-view-model-wiz__metadata-text')]
      .map(e => e.textContent.trim())
      .filter(t => t.length > 0 && t.length < 50);
    const viewsRe = /^[\d.,]+\s*[KMBkmb]?\s*(views?|visualiza|vues|vistas|visualizzazioni|aufrufe|次觀看|次观看|觀看|观看|회|ครั้ง)/i;
    const viewsText = allText.find(t => viewsRe.test(t)) ||
                      allText.find(t => /^[\d.,]+\s*(mil|mi|bi)\s*(views?|visualiza|vues|vistas)/i.test(t));
    if (!viewsText) continue;
    out.push(viewsText);
  }
  return out;
}
