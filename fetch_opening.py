#!/usr/bin/env python3
"""Fetch UZCE opening auction rate (USD/UZS) and write opening.json.

Runs mid-morning, after the ~10:20 auction opens. The exchange's weighted-average
rate at that point is an early, market-driven preview of where the soum will settle
before the official CBU rate is published later in the day.

Source: cabinet.uzrvb.uz (JSC Uzbek Republican Currency Exchange).
In the daily series, 'close' is the weighted-average rate for that trading day.
"""
import json, urllib.request, datetime

URL = "https://cabinet.uzrvb.uz/api/usd_rate?type=daily"
OUT = "opening.json"

def get(u):
    return urllib.request.urlopen(
        urllib.request.Request(u, headers={"User-Agent": "fx-archive/1.0"}), timeout=30).read()

def main():
    rows = [d for d in json.loads(get(URL))["data"] if d.get("close")]
    last, prev = rows[-1], rows[-2]
    rate = float(last["close"])          # current weighted-average (mid-morning ≈ opening auction)
    prev_close = float(prev["close"])    # previous trading day's weighted-average
    out = {
        "date": last["time"][:10],
        "rate": round(rate, 2),
        "prev_close": round(prev_close, 2),
        "som_change": round(rate - prev_close, 2),          # change in so'm per USD
        "pct": round((prev_close / rate - 1) * 100, 2),     # soum's move (+ = soum stronger)
        "high": float(last.get("high") or rate),
        "low": float(last.get("low") or rate),
        "updated": datetime.datetime.utcnow().isoformat(timespec="minutes") + "Z",
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"opening {out['date']}: {out['rate']} so'm  soum {out['pct']:+.2f}%")

if __name__ == "__main__":
    main()
