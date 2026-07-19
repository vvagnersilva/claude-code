// Paste this into `browser_evaluate` to scroll a results page one step and
// report how many result cards are currently loaded. Call it repeatedly
// (wait ~1.2s between calls) until the count reaches your target.
() => {
  window.scrollBy(0, document.documentElement.scrollHeight);
  return { loaded: document.querySelectorAll('ytd-video-renderer').length };
}
