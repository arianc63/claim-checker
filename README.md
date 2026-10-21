# ClaimChecker — on-chain fact-checking with GenLayer

An Intelligent Contract that checks a claim against a live web page. Validators fetch the page, ask an LLM for a verdict (TRUE / FALSE / UNVERIFIABLE), and must agree on the verdict through GenLayer's optimistic-democracy consensus. Verdicts are stored on-chain.

**Problem:** a single LLM answer can't be trusted. Here the verdict depends on live, authoritative web data and multi-validator consensus, not one model's output.

## Files
- `contract.py` — the Intelligent Contract
- `frontend/index.html` — UI using `genlayer-js` (reads and writes the contract)

## How to use
1. Open GenLayer Studio, paste `contract.py`, deploy, copy the address.
2. Open the site, paste the address, enter a claim + source URL, click **Check claim**.
3. Wait for consensus; the verdict appears under "Recent verdicts".

## Example
Claim: "The Eiffel Tower is 330 m tall" — Source: its Wikipedia page → TRUE.
