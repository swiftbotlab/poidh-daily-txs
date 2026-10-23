#!/usr/bin/env python3
"""Build data/daily.json + data/daily.csv: poidh v3 transactions per day (UTC) on Ethereum, Arbitrum and Base since 2026-01-01.

Source: poidh's public indexer (https://indexer.poidh.xyz/api/v1/transactions), which records every contract transaction it
indexes (bounty created / joined, claim created, submitted for vote, voted, resolved, accepted, canceled) with its tx hash
and timestamp. A transaction counts for the v3 contracts when its bounty belongs to v3:
  Ethereum 0xE731dFadBFf20542E10D09D26Fc71445C70d4232 (all indexed bounties; v3 is the only mainnet contract indexed)
  Base     0x5555Fa783936C260f77385b4E153B9725feF1719 (indexer bounty id >= 986, the v3 bounty with onChainId 0, 2026-01-20)
  Arbitrum 0x5555Fa783936C260f77385b4E153B9725feF1719 (indexer bounty id >= 180, the v3 bounty with onChainId 0, 2026-01-20)
One row per distinct tx hash (a tx that logs two actions is counted once). Stdlib only; no keys."""
import csv, json, os, time, urllib.request
from datetime import datetime, timezone, date, timedelta

API = "https://indexer.poidh.xyz/api/v1"
CHAINS = [  # key, chainId, label, contract, first v3 bounty id in the indexer
    ("ethereum", 1, "Ethereum", "0xE731dFadBFf20542E10D09D26Fc71445C70d4232", 0),
    ("arbitrum", 42161, "Arbitrum", "0x5555Fa783936C260f77385b4E153B9725feF1719", 180),
    ("base", 8453, "Base", "0x5555Fa783936C260f77385b4E153B9725feF1719", 986),
]
START = date(2026, 1, 1)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "poidh-daily-txs/1.0 (+github.com/swiftbotlab/poidh-daily-txs)"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read(20_000_000))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def check_boundary(chain_id, first_v3):
    """Fail loudly if the v3 boundary assumption ever stops holding."""
    rows = get(f"{API}/bounties?chainId={chain_id}&onChainId=0")
    ids = sorted(b["id"] for b in rows)
    assert first_v3 in ids, f"chain {chain_id}: expected a bounty id {first_v3} with onChainId 0, got {ids}"


def fetch(chain_id):
    rows, off = [], 0
    while True:
        page = get(f"{API}/transactions?chainId={chain_id}&limit=100&offset={off}")
        rows += page
        if len(page) < 100:
            return rows
        off += 100


def main():
    start_ts = int(datetime(START.year, START.month, START.day, tzinfo=timezone.utc).timestamp())
    today = datetime.now(timezone.utc).date()
    days = [START + timedelta(d) for d in range((today - START).days + 1)]
    per = {k: {d.isoformat(): set() for d in days} for k, *_ in CHAINS}
    meta = []
    for key, cid, label, addr, first_v3 in CHAINS:
        if first_v3:
            check_boundary(cid, first_v3)
        rows = fetch(cid)
        n = 0
        for r in rows:
            ts, bid = r.get("timestamp"), r.get("bountyId")
            if ts is None or ts < start_ts or bid is None or bid < first_v3:
                continue
            d = datetime.fromtimestamp(ts, timezone.utc).date().isoformat()
            if d in per[key]:
                per[key][d].add(r["tx"].lower())
                n += 1
        meta.append({"key": key, "label": label, "chainId": cid, "contract": addr, "indexedRows": len(rows), "v3RowsSince2026": n})
    out = []
    for d in days:
        iso = d.isoformat()
        row = {"date": iso}
        for key, *_ in CHAINS:
            row[key] = len(per[key][iso])
        row["total"] = sum(row[k] for k, *_ in CHAINS)
        out.append(row)
    os.makedirs(OUT, exist_ok=True)
    doc = {"generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "source": f"{API}/transactions",
           "chains": meta, "days": out}
    tmp = os.path.join(OUT, "daily.json.tmp")
    json.dump(doc, open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, os.path.join(OUT, "daily.json"))
    with open(os.path.join(OUT, "daily.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date_utc", "ethereum", "arbitrum", "base", "total"])
        for r in out:
            w.writerow([r["date"], r["ethereum"], r["arbitrum"], r["base"], r["total"]])
    tot = sum(r["total"] for r in out)
    print(f"{len(out)} days, {tot} transactions; " + ", ".join(f"{m['label']} {sum(r[m['key']] for r in out)}" for m in meta))


if __name__ == "__main__":
    main()
