# poidh transactions per day

Live dashboard: **https://swiftbotlab.github.io/poidh-daily-txs/**

Daily transactions on the poidh v3 contracts since January 1, 2026:

| Chain | Contract |
|---|---|
| Ethereum | `0xE731dFadBFf20542E10D09D26Fc71445C70d4232` |
| Arbitrum | `0x5555Fa783936C260f77385b4E153B9725feF1719` |
| Base | `0x5555Fa783936C260f77385b4E153B9725feF1719` |

- `build.py` (Python stdlib, no keys) reads poidh's public indexer (`https://indexer.poidh.xyz/api/v1/transactions`), keeps transactions on v3 bounties, and counts distinct transaction hashes per UTC day and chain. It writes `data/daily.json` and `data/daily.csv`.
- `.github/workflows/daily.yml` reruns it every day at 00:20 UTC, commits the data and redeploys the page with GitHub Pages.
- `index.html` is a single static page (no build step, no external scripts):
  - stacked daily or weekly bars **by chain** or **by action** (claims, bounties, funding, voting, accepted), or a **cumulative** line;
  - 7 d / 30 d / 90 d / since-Jan-1 ranges plus any custom date range, and a 7-day average line;
  - click a legend chip to hide or show a chain or action; hover for the numbers;
  - **click any bar (or table row) to list that day's transactions**, each linked to its block explorer and its poidh bounty;
  - light/dark theme, works on phones, and the URL keeps the current view so it can be shared;
  - the full daily table plus CSV and JSON downloads (`data/txs.json` holds every transaction).

Notes: v3 went live on Arbitrum and Base on 2026-01-20 and on Ethereum on 2026-05-14. Transactions sent through smart wallets are counted. Withdrawals are not indexed per bounty and are not included.

Built by Swift Bot Labs.
