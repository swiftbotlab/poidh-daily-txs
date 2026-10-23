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
- `index.html` is a single static page: stacked daily or weekly bars by chain, 30-day / 90-day / since-Jan-1 ranges, hover details, and the full table with CSV download.

Notes: v3 went live on Arbitrum and Base on 2026-01-20 and on Ethereum on 2026-05-14. Transactions sent through smart wallets are counted. Withdrawals are not indexed per bounty and are not included.

Built by Swift Bot Labs.
