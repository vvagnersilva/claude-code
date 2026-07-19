// Paste this function into the `browser_evaluate` tool on a YouTube search
// results page. It returns every loaded result card as a plain object.
// Run it AFTER you have scrolled enough times to load 150+ cards.
() => {
  const cards = [...document.querySelectorAll('ytd-video-renderer')];
  return cards.map(card => {
    const titleEl   = card.querySelector('a#video-title');
    const channelEl = card.querySelector('ytd-channel-name a');
    const metaSpans = [...card.querySelectorAll('#metadata-line span')]
      .map(s => s.textContent.trim()).filter(Boolean);
    const lengthEl  = card.querySelector(
      'ytd-thumbnail-overlay-time-status-renderer #text, .badge-shape-wiz__text');
    const href = titleEl ? titleEl.getAttribute('href') || '' : '';
    const qs   = href.includes('?') ? href.split('?')[1] : '';
    const vid  = new URLSearchParams(qs).get('v') || '';
    const viewsText = metaSpans.find(t => /view/i.test(t)) || metaSpans[0] || '';
    const whenText  = metaSpans.find(t => /(ago|hour|day|week|month|year)/i.test(t)) || metaSpans[1] || '';
    return {
      title:       titleEl ? titleEl.textContent.trim() : '',
      channel:     channelEl ? channelEl.textContent.trim() : '',
      channelHref: channelEl ? channelEl.href : '',
      viewsText,
      whenText,
      length:      lengthEl ? lengthEl.textContent.trim() : '',
      videoId:     vid,
      href:        href.startsWith('http') ? href : 'https://www.youtube.com' + href
    };
  }).filter(v => v.videoId);
}
