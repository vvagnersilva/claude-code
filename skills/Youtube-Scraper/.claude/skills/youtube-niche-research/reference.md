# Reference — YouTube Niche Research

## Search filter (`sp`) codes

YouTube encodes search filters in the `sp` query parameter. These are stable
across time. Build the URL as:

```
https://www.youtube.com/results?search_query=<URL-ENCODED KEYWORD>&sp=<CODE>
```

| Window      | `sp` code        | Meaning                                        |
|-------------|------------------|------------------------------------------------|
| This month  | `CAISBAgEGAI%3D` | Sort = View count · Upload = This month · Long |
| This week   | `CAISBAgDGAI%3D` | Sort = View count · Upload = This week · Long  |
| Today       | `CAISBAgCGAI%3D` | Sort = View count · Upload = Today · Long      |
| This year   | `CAISBAgFGAI%3D` | Sort = View count · Upload = This year · Long  |

The 5th decoded byte controls the date window: `02`=today, `03`=this week,
`04`=this month, `05`=this year. "Long" duration means 20 min+.

> YouTube often ignores the view-count sort when combined with other filters.
> **Never trust the on-page order** — always extract everything, parse the view
> counts yourself, and sort in code.

## Parsing `viewsText` → integer

`viewsText` looks like `"1.2M views"`, `"834K views"`, `"12,034 views"`,
`"1.1B views"`. Convert to an absolute integer:

- Strip the word `views` and whitespace.
- Suffix `K` → ×1,000 · `M` → ×1,000,000 · `B` → ×1,000,000,000.
- No suffix → remove thousands separators (`,` or `.` depending on locale) and
  parse directly.
- Localized strings: `"mil"`/`"mi"` (pt), `"k"`/`"M"` lowercase, etc. — handle the
  numeric part and the magnitude word/letter.

## Parsing `whenText` → daysAgo

`whenText` looks like `"6 days ago"`, `"2 weeks ago"`, `"1 month ago"`,
`"3 hours ago"`. Convert to a day count:

- `hour(s)` / `minute(s)` / `today` → `0`
- `day(s)` → the number
- `week(s)` → number × 7
- `month(s)` → number × 30
- `year(s)` → number × 365

Handle non-English equivalents too (e.g. pt: `dias`, `semanas`, `meses`).

## Performance metric

For each video: `performance = videoViews / channelAvg`, rounded to 1 decimal.
`channelAvg` is the mean of the 12 most recent regular videos on the channel.
If the average cannot be computed, `performance = null` → display "n/a".

Color thresholds: `> 1.5` green · `1.0–1.5` amber · `< 1.0` red · `null` grey.

## Troubleshooting

- **Blank thumbnails** — you screenshotted before the image decoded. Always run
  `scripts/prepare-thumbnail.js` first and wait for `{ok:true}`.
- **Cookie / consent wall** — if YouTube shows a consent dialog, accept or reject
  it with `browser_click` before extracting, then continue.
- **Too few results load** — keep scrolling; some niches simply have fewer
  long videos this week. Collect what exists and note it in the final summary.
- **Channel `/videos` empty** — some channels use `@handle` URLs; ensure the
  href ends in `/videos`. If still empty, set `performance = null`.
- **Selectors changed** — YouTube updates its DOM. If `ytd-video-renderer`
  yields nothing, inspect the page with `browser_snapshot` and adapt selectors.
