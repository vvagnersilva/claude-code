// Paste this into `browser_evaluate` BEFORE taking a thumbnail screenshot.
// Replace __VIDEO_ID__ with the real videoId. It scrolls the card into view
// and polls until the lazy-loaded thumbnail image is fully decoded.
// Returns {ok:true} when the thumbnail is ready to screenshot.
async () => {
  const VID  = '__VIDEO_ID__';
  const card = document.querySelector(
    `ytd-video-renderer:has(a#video-title[href*="${VID}"])`);
  if (!card) return { ok: false, reason: 'card not found' };
  card.scrollIntoView({ block: 'center' });
  const deadline = Date.now() + 8000;
  while (Date.now() < deadline) {
    const img = card.querySelector('img');
    if (img && img.complete && img.naturalWidth > 10) {
      await new Promise(r => setTimeout(r, 300)); // settle
      return { ok: true };
    }
    await new Promise(r => setTimeout(r, 250));
  }
  return { ok: false, reason: 'thumbnail did not load within 8s' };
}
