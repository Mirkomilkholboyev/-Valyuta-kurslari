#!/usr/bin/env python3
"""Append today's USD exchange rates to history.json.
Runs daily via GitHub Actions. Builds the history the free feeds don't keep,
so every currency (including UZS, KZT and the region) gets change columns over time.
"""
import json, os, urllib.request, datetime

URL = "https://open.er-api.com/v6/latest/USD"   # free, no key, ~161 currencies
HIST = "history.json"

def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "fx-archive/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("result") != "success":
        raise SystemExit("rate feed returned an error")

    rates = data["rates"]                        # {code: units_per_USD}
    day = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    hist = {}
    if os.path.exists(HIST):
        with open(HIST, encoding="utf-8") as f:
            hist = json.load(f)

    hist[day] = {k: round(v, 6) for k, v in rates.items()}

    with open(HIST, "w", encoding="utf-8") as f:
        json.dump(hist, f, separators=(",", ":"), sort_keys=True)

    print(f"saved {day}: {len(rates)} currencies ({len(hist)} days on file)")

if __name__ == "__main__":
    main()
