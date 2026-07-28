"""Shared arm machinery: actor call with one-shot retry, the proposal pool builder, the
predeclared vote/aggregator selectors (with eval-only audit metadata), and bo3's
visible_rank. Ported from bench_v2 arms.py. Selectors attach `_proposals` to the chosen
action (popped in episode.py, never reaches the agent).
"""
from __future__ import annotations
import json
import re
import statistics
from collections import Counter

from bench_v3.core.actions import extract_json_action
from bench_v3.prompts.render import base_user
from bench_v3.prompts.base_actor import FORMAT_RETRY_MSG


def obs_user(obs) -> str:
    return base_user(json.dumps(obs, ensure_ascii=False))


def ask(model, system, user, retry):
    msg = user if not retry else (user + "\n\n" + FORMAT_RETRY_MSG)
    return extract_json_action(model(system, msg))


def propose_all(model, systems, labels, obs):
    """Run each system prompt once; one record per candidate (eval-side). Selection
    consumes only the parsed subset; the full pool is preserved for D3/oracle@3."""
    recs = []
    for i, (s, lab) in enumerate(zip(systems, labels)):
        n0, pt0, ct0 = getattr(model, "calls", 0), getattr(model, "pt", 0), getattr(model, "ct", 0)
        txt = model(s, obs_user(obs)) or ""
        act = extract_json_action(txt)
        recs.append({"index": i, "label": lab, "action": act, "parse_ok": act is not None,
                     "raw": (None if act is not None else txt[:400]),
                     "tokens": {"calls": getattr(model, "calls", 0) - n0,
                                "pt": getattr(model, "pt", 0) - pt0, "ct": getattr(model, "ct", 0) - ct0}})
    return recs


def _cand_log(recs):
    return [{"index": r["index"], "label": r["label"], "parse_ok": r["parse_ok"],
             "action": r["action"], "raw": r["raw"], "tokens": r["tokens"]} for r in recs]


def select_vote(recs):
    """Majority type; median params within the winner; first parsed on a tie."""
    props = [r for r in recs if r["parse_ok"]]
    if not props:
        return None, {"method": "vote", "note": "no parsable proposals"}
    types = [p["action"]["type"] for p in props]
    cnt = Counter(types); top = cnt.most_common(1)[0][1]
    winners = [t for t, c in cnt.items() if c == top]
    if len(winners) > 1:
        return dict(props[0]["action"]), {"method": "vote", "outcome": "no_majority_first",
                                          "winner_type": props[0]["action"]["type"],
                                          "source_indices": [props[0]["index"]]}
    win = winners[0]
    group = [p for p in props if p["action"]["type"] == win]
    rep = dict(group[0]["action"])
    for pf in ("volume_ml", "target_volume_ml"):
        vals = [p["action"][pf] for p in group if isinstance(p["action"].get(pf), (int, float))]
        if vals:
            rep[pf] = round(statistics.median(vals), 4)
    return rep, {"method": "vote", "winner_type": win, "median_synth": True,
                 "source_indices": [p["index"] for p in group]}


def select_agg(judge_model, obs, recs, rng, agg_system):
    """Anonymize + shuffle candidates; judge picks {"choice": n}; falls back to first."""
    props = [r for r in recs if r["parse_ok"]]
    if not props:
        return None, {"method": "agg", "note": "no parsable proposals"}
    order = list(range(len(props)))
    rng.shuffle(order)
    shuffled = [props[i] for i in order]
    lines = [f"{i}. {json.dumps({k: v for k, v in p['action'].items() if k != 'rationale'}, ensure_ascii=False)}"
             for i, p in enumerate(shuffled, 1)]
    user = (f"Current observation (JSON):\n{json.dumps(obs, ensure_ascii=False)}\n\n"
            f"Candidate actions:\n" + "\n".join(lines) + '\n\nChoose one. Output {"choice": n}. JSON only.')
    n0, pt0, ct0 = getattr(judge_model, "calls", 0), getattr(judge_model, "pt", 0), getattr(judge_model, "ct", 0)
    txt = judge_model(agg_system, user) or ""
    jtok = {"calls": getattr(judge_model, "calls", 0) - n0, "pt": getattr(judge_model, "pt", 0) - pt0,
            "ct": getattr(judge_model, "ct", 0) - ct0}
    m = re.findall(r'"choice"\s*:\s*([1-9])', txt) or re.findall(r"\b([1-3])\b", txt)
    if m:
        n = int(m[-1]) - 1
        if 0 <= n < len(shuffled):
            ch = shuffled[n]
            return dict(ch["action"]), {"method": "agg", "choice_num": n + 1, "source_index": ch["index"],
                                        "agg_raw": txt[:200], "judge_tokens": jtok}
    ch = shuffled[0]
    return dict(ch["action"]), {"method": "agg", "choice_num": None, "fallback_first": True,
                                "source_index": ch["index"], "agg_raw": txt[:200], "judge_tokens": jtok}


def attach_proposals(chosen, arm, recs, meta):
    if isinstance(chosen, dict):
        chosen["_proposals"] = {"arm": arm, "candidates": _cand_log(recs), "selection": meta}
    return chosen


def visible_rank(ep, target):
    """bo3 episode-level rank using VISIBLE quantities only: accept > handoff > unmanaged,
    tie-break by last visible measurement deviation from target (smaller better). No truth."""
    tier = {"accept_batch": 2, "abort_and_handoff": 1}.get(ep.terminal, 0)
    last_meas = None
    for e in ep.action_log:
        if e.get("committed") and (e.get("result") or {}).get("measured_concentration_M") is not None:
            last_meas = e["result"]["measured_concentration_M"]
    dev = abs(last_meas - target) if last_meas is not None else 1e9
    return (tier, -dev)
