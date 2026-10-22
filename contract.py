# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class ClaimChecker(gl.Contract):
    """Fact-checks a claim against a live web page via validator consensus.
    v2: re-checking with verdict history, filtering by verdict, and stats."""

    verdicts: TreeMap[str, str]
    count: u256

    def __init__(self):
        self.count = u256(0)

    def _verify(self, claim: str, source_url: str) -> dict:
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
            raw = raw.replace(chr(96) * 3 + "json", "").replace(chr(96) * 3, "").strip()
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
        return json.loads(result)

    @gl.public.write
    def check_claim(self, claim: str, source_url: str) -> str:
        info = self._verify(claim, source_url)
        claim_id = str(self.count)
        self.verdicts[claim_id] = json.dumps(
            {
                "id": claim_id,
                "claim": claim,
                "source_url": source_url,
                "verdict": info["verdict"],
                "reason": info["reason"],
                "history": [info["verdict"]],
                "rechecks": 0,
            }
        )
        self.count = u256(int(self.count) + 1)
        return claim_id

    @gl.public.write
    def recheck_claim(self, claim_id: str) -> str:
        raw = self.verdicts.get(claim_id, "")
        if raw == "":
            raise Exception("claim not found")
        item = json.loads(raw)
        info = self._verify(item["claim"], item["source_url"])
        item["verdict"] = info["verdict"]
        item["reason"] = info["reason"]
        item["history"].append(info["verdict"])
        item["rechecks"] = int(item["rechecks"]) + 1
        self.verdicts[claim_id] = json.dumps(item)
        return info["verdict"]

    @gl.public.view
    def get_count(self) -> int:
        return int(self.count)

    @gl.public.view
    def get_claim(self, claim_id: str) -> str:
        return self.verdicts.get(claim_id, "")

    @gl.public.view
    def get_claims_by_verdict(self, verdict: str) -> str:
        wanted = verdict.upper()
        out = []
        for i in range(int(self.count)):
            raw = self.verdicts.get(str(i), "")
            if raw == "":
                continue
            item = json.loads(raw)
            if item["verdict"] == wanted:
                out.append(item)
        return json.dumps(out[-20:])

    @gl.public.view
    def get_stats(self) -> str:
        stats = {"total": 0, "TRUE": 0, "FALSE": 0, "UNVERIFIABLE": 0, "rechecked": 0, "flipped": 0}
        for i in range(int(self.count)):
            raw = self.verdicts.get(str(i), "")
            if raw == "":
                continue
            item = json.loads(raw)
            stats["total"] += 1
            stats[item["verdict"]] += 1
            if int(item["rechecks"]) > 0:
                stats["rechecked"] += 1
            if len(set(item["history"])) > 1:
                stats["flipped"] += 1
        return json.dumps(stats)
