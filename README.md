# Global FX Board — currencies vs the US dollar

A single-page board showing every national currency against the US dollar,
with change over 1 day, 1 week, month-to-date and year-to-date, a ranked
diverging chart, search, a Central Asia & Caucasus filter, and an English/Uzbek toggle.

## Files
- `index.html` — the whole site (open it in a browser, or host it as-is)
- `update_rates.py` — appends today's rates to `history.json`
- `.github/workflows/update-rates.yml` — runs the script once a day
- `history.json` — your growing rate archive (starts empty)

## How the data works
- **Today's rate** for ~161 currencies: the free ExchangeRate-API open endpoint (no key).
- **Change columns** for ~31 major currencies: official ECB rates via Frankfurter (no key),
  which has full daily history immediately.
- **Change columns for every other currency** (UZS, KZT, KGS, TJS, RUB…): computed from
  your own `history.json`, which fills in one day at a time. You need ~1 week of runs for
  the 1-week column, and you cross a month/year boundary before those columns appear for
  the region. This is unavoidable — no free feed keeps daily history for these currencies,
  so the archive *is* the history.

Baselines: 1 day = previous business day · 1 week = ~7 days earlier ·
Month = close of last month · Year = close of last year.
Positive = the currency gained against the dollar.

## Setup (free, ~5 minutes)
1. Create a new GitHub repository and upload these files (keep the folder structure).
2. In **Settings → Pages**, set Source = `main` branch, root. Your board goes live at
   `https://<username>.github.io/<repo>/`.
3. In the **Actions** tab, enable workflows. Open **Daily FX archive → Run workflow** once
   to write the first day into `history.json`. After that it runs itself every day.

That's it — the page reads `history.json` from the same folder, so the region's change
columns light up automatically as the archive grows.

## Going further for Central Asia
For the most authoritative regional numbers, add a fetch to each central bank in
`update_rates.py` (e.g. the CBU JSON feed `https://cbu.uz/uz/arkhiv-kursov-valyut/json/`
for UZS) and merge those into the daily snapshot. Central-bank feeds usually can't be
called from the browser directly (no CORS), which is exactly why the daily job fetches
them server-side.
