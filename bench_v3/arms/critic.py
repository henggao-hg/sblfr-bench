"""A3 free_critic / A4 thin_critic / A10 self+rubric. actor drafts; a (different) critic
approves or asks for one revision. The critic verdict/critique/principle-refs/tokens are
recorded eval-only via `_critic` (popped in episode.py, never reaches the agent).
Decision flow identical to bench_v2 arms.policy_critic.
"""
from __future__ import annotations
import json
import re

from bench_v3.arms.base import obs_user, ask
from bench_v3.core.actions import extract_json_action
from bench_v3.prompts.base_actor import BASE_SYSTEM
from bench_v3.prompts.critic import FREE_CRITIC_SYSTEM, THIN_CRITIC_SYSTEM, revise_msg


def policy_critic(actor_model, critic_model, rubric_in_critic):
    csys = THIN_CRITIC_SYSTEM if rubric_in_critic else FREE_CRITIC_SYSTEM
    variant = "thin" if rubric_in_critic else "free"

    def f(obs, retry=False):
        draft = ask(actor_model, BASE_SYSTEM, obs_user(obs), retry)
        if draft is None:
            return None
        cuser = (f"Current observation (JSON):\n{json.dumps(obs, ensure_ascii=False)}\n\n"
                 f"Proposed action: {json.dumps(draft, ensure_ascii=False)}")
        n0, pt0, ct0 = getattr(critic_model, "calls", 0), getattr(critic_model, "pt", 0), getattr(critic_model, "ct", 0)
        verdict_txt = critic_model(csys, cuser) or ""
        ctok = {"calls": getattr(critic_model, "calls", 0) - n0,
                "pt": getattr(critic_model, "pt", 0) - pt0, "ct": getattr(critic_model, "ct", 0) - ct0}
        raw = verdict_txt.strip()
        vobj = None
        if not raw:
            status = "empty"
        else:
            try:
                vobj = json.loads(re.findall(r"\{.*\}", raw.replace("\n", " "))[-1])
                status = vobj.get("verdict", "approve")
                if status not in ("approve", "revise"):
                    status = "parse_fail"
            except Exception:
                status = "parse_fail"
        crit = (vobj or {}).get("critique", "") if isinstance(vobj, dict) else ""
        refs = sorted({int(x) for x in re.findall(r"principles?\s*#?\s*(\d+)", crit, re.I)})
        cinfo = {"critic_model": getattr(critic_model, "name", "?"), "critic_prompt_variant": variant,
                 "critic_verdict": status, "critic_critique": crit, "critic_principle_refs": refs,
                 "critic_tokens": ctok, "critic_raw_text": (raw[:600] if status != "approve" else None)}
        if status != "revise":
            draft["_critic"] = cinfo
            return draft
        final = extract_json_action(actor_model(BASE_SYSTEM, obs_user(obs) + "\n\n" + revise_msg(crit)))
        if isinstance(final, dict):
            final["_critic"] = cinfo
        return final   # may be None -> env retries (same as bench_v2)
    return f
