# { "Depends": "py-genlayer:latest" }
from genlayer import *
import json


class ClaimChecker(gl.Contract):
    """Fact-checks a claim against a live web page via validator consensus."""

    verdicts: TreeMap[str, str]
    count: u256

    def __init__(self):
        self.count = u256(0)

    @gl.public.write
    def check_claim(self, claim: str, source_url: str) -> str:
        def run() -> str:
            page = gl.nondet.web.render(source_url, mode="text")
            prompt = f"""You are a strict fact-checker.
CLAIM: {claim}

SOURCE PAGE CONTENT (may be truncated):
{page[:6000]}

Decide using ONLY the source above.
Answer with JSON only, no markdown:
{{"verdict": "TRUE" | "FALSE" | "UNVERIFIABLE", "reason": "max 2 short sentences"}}"""
            raw = gl.nondet.exec_prompt(prompt)
            raw = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)
            verdict = str(data.get("verdict", "UNVERIFIABLE")).upper()
            if verdict not in ("TRUE", "FALSE", "UNVERIFIABLE"):
                verdict = "UNVERIFIABLE"
            return json.dumps(
                {"verdict": verdict, "reason": str(data.get("reason", ""))[:300]},
                sort_keys=True,
            )

        result = gl.eq_principle.prompt_comparative(
            run,
            "The 'verdict' field must be identical. The 'reason' may be worded differently.",
        )
        info = json.loads(result)
        claim_id = str(self.count)
        self.verdicts[claim_id] = json.dumps(
            {
                "id": claim_id,
                "claim": claim,
                "source_url": source_url,
                "verdict": info["verdict"],
                "reason": info["reason"],
            }
        )
        self.count = u256(int(self.count) + 1)
        return claim_id

    @gl.public.view
    def get_count(self) -> int:
        return int(self.count)

    @gl.public.view
    def get_claim(self, claim_id: str) -> str:
        return self.verdicts.get(claim_id, "")
