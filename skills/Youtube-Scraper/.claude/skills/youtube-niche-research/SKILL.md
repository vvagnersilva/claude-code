---
name: youtube-niche-research
description: Research YouTube for a niche/keyword and produce an interactive, fully self-contained HTML report of the top videos this month and this week — with embedded thumbnails, absolute view counts, "views vs channel average" performance scores, and an interactive ranking control. Use whenever the user wants YouTube market research, niche analysis, content-gap research, or competitor video analysis for a search term in any language.
---

# YouTube Niche Research → Interactive HTML Report

Research YouTube for a `KEYWORD` and produce one interactive, fully self-contained
HTML report. Use the **Playwright MCP browser tools** and track progress with a
todo list. Follow every step precisely.

## 🌐 Language protocol

Internal directives (this file) are English — for you, the agent. **Everything
the user sees must be in Brazilian Portuguese**: progress messages, questions,
the final summary, and the HTML report (the template already has Portuguese
labels — keep them). Video titles and channel names stay in whatever language
YouTube returns. Technical identifiers (paths, commands) may stay English.

## Step 0a — Preflight (run before anything else)

This skill needs the **Playwright MCP browser tools** (`mcp__playwright__*`).

1. Check whether those tools are available in this session.
2. If they are **not** available, do **not** try to scrape YouTube with
   `curl`/`fetch`. Instead tell the user, in Portuguese, that the environment is
   not set up yet and run the **`setup`** skill (or instruct them to run
   `/setup`). After setup finishes and the session is restarted, resume here.
3. If the tools are available, continue to Step 0.

## Inputs

Determine these before starting:

- **`KEYWORD`** — the niche / search term (any language). If the user invoked the
  skill with text after it (e.g. `/youtube-niche-research arquitetura`), that text
  is the keyword. Otherwise ask the user for it.
- **`OUTPUT_DIR`** — where to save the report, **relative to this repository's
  root**. Default `reports/`. Always keep output inside the repo so the project
  stays fully portable — never write to a path outside the repository.

## Bundled files (read them when you reach the relevant step)

- `scripts/scroll-page.js` — scroll a results page and count loaded cards.
- `scripts/extract-results.js` — extract all result cards from a search page.
- `scripts/extract-channel-views.js` — extract recent view counts on a channel.
- `scripts/prepare-thumbnail.js` — scroll + poll a card so its thumbnail is loaded.
- `scripts/inject-data.js` — **MANDATORY** helper that injects the DATA object
  into the report template (do not write your own regex — see Step 5).
- `scripts/serve-report.sh` — start a local HTTP server so Playwright can load
  the generated report (file:// URLs are blocked by the MCP browser).
- `scripts/verify-report-mcp.js` — Playwright MCP snippet used in Step 7 to
  validate the rendered report.
- `assets/report-template.html` — the HTML report template to fill in.
- `reference.md` — `sp` filter codes, view/date parsing rules, troubleshooting.

## Step 0 — Setup

1. Resolve `OUTPUT_DIR` relative to the repository root (the current working
   directory when Claude Code starts in this repo). Default is `reports/`.
   Create the folder if it does not exist. Never write outside the repository.
2. Slugify `KEYWORD`: lowercase, trim, spaces and non-alphanumerics → `-`.
3. Final report path: `<OUTPUT_DIR>/youtube-report-<slug>.html` (e.g.
   `reports/youtube-report-<slug>.html`).
4. Create a todo list covering steps 1–6.

## Step 1 — Collect: Top 30 of THIS MONTH

1. Navigate to `https://www.youtube.com/results?search_query=<KEYWORD>&sp=CAISBAgEGAI%3D`
   (URL-encode the keyword). This filter = Sort by view count · Upload this month ·
   Long videos (20 min+).
2. **Do not trust the on-page order** — YouTube often ignores the view-count sort.
   Scroll the page ~8–10 times (≈1.2 s between scrolls) using `scripts/scroll-page.js`
   until **≥ 150** `ytd-video-renderer` elements are loaded.
3. Run `scripts/extract-results.js` via `browser_evaluate` to extract every card:
   `title`, `channel`, `channelHref`, `viewsText`, `whenText`, `length`, `videoId`,
   `href`.
4. Parse each `viewsText` into an absolute integer (see `reference.md`).
5. Sort by parsed views descending, keep the **top 30** → set `MONTH`.

## Step 2 — Collect: Top 15 of THIS WEEK

1. Navigate to `https://www.youtube.com/results?search_query=<KEYWORD>&sp=CAISBAgDGAI%3D`
   (same filters, Upload = this week).
2. Scroll and extract the same way until **≥ 100** results are loaded.
3. Sort by parsed views descending, keep the **top 15** → set `WEEK`.

## Step 3 — Compute "views vs channel average" performance

For every **unique channel** across `MONTH` ∪ `WEEK` (dedupe — never fetch a
channel twice):

1. Navigate to `<channelHref>/videos`.
2. Wait for load, scroll once, run `scripts/extract-channel-views.js` to get the
   view counts of the **12 most recent regular videos** (Shorts and live streams
   excluded).
3. `channelAvg` = mean of those parsed view counts.
4. For each video on that channel: `performance = videoViews / channelAvg`,
   rounded to 1 decimal. If no average can be obtained → `performance = null`
   ("n/a"). Record any such channels for the final summary.

## Step 4 — Capture thumbnail screenshots (respect lazy-loading!)

YouTube lazy-loads thumbnails — capturing too early yields a blank image. For
**each** video in both sets:

1. Be on the search results page that contains the card. Run
   `scripts/prepare-thumbnail.js` (replace `__VIDEO_ID__` with the real id) and
   wait until it returns `{ok:true}`.
2. Take a **thumbnail-only** element screenshot of the selector
   `ytd-video-renderer:has(a#video-title[href*="<videoId>"]) ytd-thumbnail`.
3. Read the PNG back and convert it to a base64 `data:image/png;base64,...` URI so
   the report needs no external image folder.

Tip: capture all `MONTH` thumbnails while on the month page, all `WEEK`
thumbnails while on the week page — avoids re-navigating.

## Step 5 — Build the HTML report

**Use the bundled `scripts/inject-data.js` — do not hand-roll a regex.** A naïve
regex over `/\*__DATA_START__\*\/[\s\S]*?\/\*__DATA_END__\*\//` can match the
literal marker strings if they happen to appear elsewhere in the template
(e.g. an HTML comment that documents them), corrupting the file silently while
the template's *example* `DATA` block remains and ends up being what the
browser renders. This already happened once; the helper exists to prevent a
repeat. See the project memory entry "Robust DATA injection".

1. Write the collected data to a temporary file `report-data.json` inside the
   repo (deleted in Step 7). Shape:

   ```js
   const DATA = {
     keyword, slug, generatedDate,            // generatedDate = today, YYYY-MM-DD
     month: [ { title, channel, channelHref, videoId, href,
                views, whenText, daysAgo, performance, channelAvg, thumb } ],
     week:  [ /* same shape */ ]
   };
   ```

   - `views` = parsed integer · `daysAgo` = integer from `whenText` ·
     `performance` = number or `null` · `thumb` = full base64 data URI.
   - Order the arrays by views descending (the template's default view).
2. Run:

   ```bash
   node .claude/skills/youtube-niche-research/scripts/inject-data.js \
       .claude/skills/youtube-niche-research/assets/report-template.html \
       report-data.json \
       <OUTPUT_DIR>/youtube-report-<slug>.html
   ```

   The script fails loudly if `REPLACE_WITH_BASE64` survives or if more than
   one `const DATA = ` declaration ends up in the output.

The template already implements: the two sections (📅 Top 30 — This Month,
🔥 Top 15 — This Week), horizontal cards with embedded thumbnail + **⬇ Download
thumbnail** and **🔗 Copy link** controls, the title/channel/metrics on the right,
rank badges (gold for 1–3), the per-section **Most viewed / Best performance**
ranking dropdown that reorders cards and renumbers ranks, the dark theme, and the
header summary strip. Do not add external scripts, fonts, or stylesheets — keep it
self-contained. Only inject `DATA`.

## Step 6 — Verify the rendered report with Playwright (mandatory)

The report is the deliverable — never report success without opening it in a
browser. The Playwright MCP server blocks `file://` URLs, so we serve the report
locally first.

1. Start the static server:

   ```bash
   bash .claude/skills/youtube-niche-research/scripts/serve-report.sh \
       <OUTPUT_DIR> 8765
   ```

2. Navigate to `http://localhost:8765/youtube-report-<slug>.html` with
   `mcp__playwright__browser_navigate`.
3. Run `scripts/verify-report-mcp.js` via `mcp__playwright__browser_evaluate`,
   first setting `window.__EXPECTED__` to:

   ```js
   { keyword: '<KEYWORD>', generatedDate: '<YYYY-MM-DD>',
     monthCount: 30, weekCount: 15 }
   ```

   (If your `week` set has fewer than 15 entries because the niche is small, set
   `weekCount` to the actual number collected — do not pad with fake data.)
4. If `ok === false`, **do not** report success. Read `errors`, fix the
   underlying issue, regenerate the report, and re-verify. Common failures:

   - `html still contains REPLACE_WITH_BASE64 placeholder` → injection used a
     bad regex or wrong path. Re-run `inject-data.js`.
   - `html still contains template example data` → the real `DATA` block was
     never replaced; the *example* `DATA` is being rendered. Re-run injection.
   - `broken thumbnails: N` → some thumbs failed to download; refetch and
     re-inject.
   - `sort toggle did not restore views order` → the template's interactive JS
     is broken; you almost certainly modified the template — revert.

## Step 7 — Finish

1. Open it with the OS default opener: `open` (macOS), `xdg-open` (Linux), or
   `start` (Windows).
2. Delete `report-data.json` (temporary).
3. Reply with: the report path, the top 3 of each set (title — channel — views),
   and any channels whose average could not be computed. Mention that the
   Playwright verification passed.

## Notes

- The **Download thumbnail** button is a standard `<a download>` link; where the
  file lands is decided by the end user's browser, not by this repo or the agent.
- "Channel average" is an approximation from a 12-video sample, not an official
  YouTube metric — say so if asked.
- If Playwright hits a YouTube consent/cookie wall, dismiss it with
  `browser_click` before extracting.
