# ClaimChecker — on-chain fact-checking with GenLayer

An Intelligent Contract that checks a claim against a live web page. Validators fetch the page, ask an LLM for a verdict (TRUE / FALSE / UNVERIFIABLE), and must agree on the verdict through GenLayer's comparative equivalence principle. Verdicts are stored on-chain.

**Problem:** a single LLM answer can't be trusted. Here the verdict depends on live web data and multi-validator consensus.

## v2 (milestone)
- `recheck_claim(claim_id)`: re-runs consensus on a stored claim, keeps the full verdict history (pages change; a verdict can flip).
- `get_claims_by_verdict(verdict)`: on-chain filtering (latest 20).
- `get_stats()`: totals per verdict, how many were re-checked, how many verdicts flipped.
- Frontend: Re-check button, verdict filter, stats bar.

## Functions
`check_claim`, `recheck_claim` (write); `get_claim`, `get_count`, `get_claims_by_verdict`, `get_stats` (view).

## Deployments
- v1: `0x048d78ce0a4CC2Adb30ef09B1EC094BE1C0513C4` (GenLayer Studio)
- v2: `0x893cd900f7E16C600605fF142f2D7362379Edc5F`
