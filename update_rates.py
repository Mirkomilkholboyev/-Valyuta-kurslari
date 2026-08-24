#!/usr/bin/env python3
"""Append today's USD exchange rates to history.json.

Priority chain per currency:
  1) The relevant central bank (authoritative). If reachable, its rate wins.
  2) The free ExchangeRate-API aggregator (fallback for everything else).

Runs daily via GitHub Actions. Each central-bank fetch is isolated in try/except,
so if one bank is down that day the aggregator value is kept and the run still
succeeds. Add more banks by writing a small fetcher and listing it in OVERLAYS.
"""
import json, os, datetime, urllib.request
import xml.etree.ElementTree as ET

HIST = "history.json"
UA = {"User-Agent": "fx-archive/1.0"}

def get(url, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()

# ---- base: aggregator, ~161 currencies, units per USD ----
def fetch_aggregator():
    data = json.loads(get("https://open.er-api.com/v6/latest/USD"))
    if data.get("result") != "success":
        raise SystemExit("aggregator returned an error")
    return {k: float(v) for k, v in data["rates"].items()}

# ---- central-bank overlays: each returns (CODE, units_per_USD) ----
def cb_uzbekistan():  # CBU — soum per USD
    arr = json.loads(get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/"))
    usd = next(x for x in arr if x["Ccy"] == "USD")
    return "UZS", float(usd["Rate"])

def cb_russia():  # CBR — rubles per USD
    d = json.loads(get("https://www.cbr-xml-daily.ru/daily_json.js"))
    u = d["Valute"]["USD"]
    return "RUB", float(u["Value"]) / float(u["Nominal"])

def cb_kazakhstan():  # NBK — tenge per USD
    root = ET.fromstring(get("https://nationalbank.kz/rss/rates_all.xml"))
    for item in root.iter("item"):
        if (item.findtext("title") or "").strip() == "USD":
            q = float(item.findtext("quant") or 1)
            return "KZT", float(item.findtext("description")) / q
    raise ValueError("USD not found in NBK feed")

def cb_kyrgyzstan():  # NBKR — som per USD
    root = ET.fromstring(get("https://www.nbkr.kg/XML/daily.xml"))
    for c in root.iter("Currency"):
        if c.get("ISOCode") == "USD":
            val = float((c.findtext("Value") or "").replace(",", "."))
            nom = float(c.findtext("Nominal") or 1)
            return "KGS", val / nom
    raise ValueError("USD not found in NBKR feed")

OVERLAYS = [cb_uzbekistan, cb_russia, cb_kazakhstan, cb_kyrgyzstan]

def main():
    rates = fetch_aggregator()
    used = []
    for fn in OVERLAYS:
        try:
            code, val = fn()
            rates[code] = round(val, 6)
            used.append(code)
        except Exception as e:
            print(f"  overlay {fn.__name__} skipped ({e}); using fallback")

    day = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    hist = {}
    if os.path.exists(HIST):
        with open(HIST, encoding="utf-8") as f:
            hist = json.load(f)
    hist[day] = {k: round(float(v), 6) for k, v in rates.items()}

    with open(HIST, "w", encoding="utf-8") as f:
        json.dump(hist, f, separators=(",", ":"), sort_keys=True)

    print(f"saved {day}: {len(rates)} currencies "
          f"(central banks: {', '.join(used) or 'none'}; {len(hist)} days on file)")

if __name__ == "__main__":
    main()
