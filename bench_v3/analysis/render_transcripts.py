"""Render an eval transcript (*.transcript.jsonl) into readable + machine exports.

  compact  : VISIBLE trace only (per step: action, verifier feedback, measurement
             result). Hides hidden truth (tib/tia) -- for quickly scanning "why
             UNMANAGED / over-recalibrate / never accept".
  detailed : compact + an EVAL-ONLY AUDIT block per step (critic verdict/critique/
             principle refs; sc3/team proposal pool + selected; per-step tokens; truth
             tib/tia + stock_accurate). Clearly fenced so eval-only fields are never
             mistaken for what the agent saw.

Writes both Markdown (readable report) and JSONL (canonical, re-computable). Reads the
transcript only -- never changes runner behavior.

usage: python -m bench_v3.analysis.render_transcripts <transcript.jsonl> [--mode compact|detailed|both] [--outdir DIR]
"""
from __future__ import annotations
import json, sys
from pathlib import Path

_EVAL_ONLY = ("rationale", "_critic", "_proposals")


def fmt(a):
    if not a:
        return "PARSE_FAIL"
    t = a.get("type", "?")
    parts = [f"{k}={a[k]}" for k in a if k not in ("type",) + _EVAL_ONLY]
    return t + (f"({', '.join(parts)})" if parts else "")


def verdict(v):
    if not v:
        return "?"
    if v.get("reason") == "unparseable":
        return "unparseable"
    if all(v.get(k) for k in ("schema_ok", "resource_ok", "invariants_ok")):
        return "ok"
    return "REJECTED: " + str(v.get("reason", "?"))


def _result_str(r):
    if not r:
        return ""
    for k in ("measured_concentration_M", "diluted_to", "transferred_to", "discarded",
              "quarantined", "recalibrated", "acknowledged", "measured_volume_ml"):
        if k in r:
            return f"{k}={r[k]}"
    return json.dumps(r, ensure_ascii=False)


def compact_record(rec):
    return {k: rec.get(k) for k in ("instance", "family", "class", "arm", "actor", "critic",
                                    "seed", "outcome", "cf_reason", "actions_used", "terminal")} | {
        "trace": [{"step": s["step"], "committed": s.get("committed"),
                   "action": fmt(s["action"]), "verifier": verdict(s.get("verifier")),
                   "result": _result_str(s.get("result"))}
                  for s in rec.get("steps", [])]}


def detailed_record(rec):
    cr = compact_record(rec)
    for s, tr in zip(rec.get("steps", []), cr["trace"]):
        tr["eval_only"] = {
            "tib": s.get("tib"), "tia": s.get("tia"), "stock_accurate": s.get("stock_accurate"),
            "tok": s.get("tok"), "rationale": (s.get("action") or {}).get("rationale"),
            "critic": s.get("critic"), "proposals": s.get("proposals")}
    return cr


def md_compact(rec):
    out = [f"## {rec.get('instance')} | {rec.get('arm')} | actor={rec.get('actor')} | seed {rec.get('seed')}",
           f"Outcome: {rec.get('outcome')}  |  CF reason: {rec.get('cf_reason')}  |  "
           f"actions: {rec.get('actions_used')}  |  terminal: {rec.get('terminal')}", "",
           "| step | action | verifier | result |", "|---|---|---|---|"]
    for s in rec.get("steps", []):
        out.append(f"| {s['step']} | {fmt(s['action'])} | {verdict(s.get('verifier'))} | {_result_str(s.get('result'))} |")
    return "\n".join(out) + "\n"


def md_detailed(rec):
    out = [md_compact(rec), "", "**EVAL-ONLY AUDIT** (not visible to the agent):", ""]
    for s in rec.get("steps", []):
        bits = [f"step {s['step']}: tib={s.get('tib')} tia={s.get('tia')} tok={s.get('tok')}"]
        c = s.get("critic")
        if c:
            bits.append(f"  critic[{c.get('critic_model')}/{c.get('critic_prompt_variant')}]: "
                        f"{c.get('critic_verdict')} refs={c.get('critic_principle_refs')} :: {c.get('critic_critique')}")
        p = s.get("proposals")
        if p:
            sel = p.get("selection", {})
            idx = sel.get("source_indices") or ([sel.get("source_index")] if sel.get("source_index") is not None else [])
            bits.append(f"  proposals[{p.get('arm')}] sel={sel.get('method')}:")
            for cnd in p.get("candidates", []):
                star = " <== SELECTED" if cnd["index"] in idx else ""
                bits.append(f"    [{cnd['label']}] {fmt(cnd['action']) if cnd['parse_ok'] else 'PARSE_FAIL'}{star}")
        rat = (s.get("action") or {}).get("rationale")
        if rat:
            bits.append(f"  rationale: {rat[:200]}")
        out.append("\n".join(bits))
    return "\n".join(out) + "\n"


HEADER = "<!-- NOTE: evaluator-side readable export. detailed mode includes EVAL-ONLY fields the agent never saw. -->\n\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = args[0]
    mode = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "both"
    outdir = Path(sys.argv[sys.argv.index("--outdir") + 1] if "--outdir" in sys.argv else Path(path).parent)
    outdir.mkdir(parents=True, exist_ok=True)
    recs = [json.loads(l) for l in open(path)]
    base = Path(path).name.replace(".transcript.jsonl", "").replace(".jsonl", "")
    modes = ["compact", "detailed"] if mode == "both" else [mode]
    for m in modes:
        recfn = compact_record if m == "compact" else detailed_record
        mdfn = md_compact if m == "compact" else md_detailed
        jl = outdir / f"{base}.{m}.jsonl"
        md = outdir / f"{base}.{m}.md"
        with open(jl, "w") as f:
            for r in recs:
                f.write(json.dumps(recfn(r), ensure_ascii=False) + "\n")
        with open(md, "w") as f:
            f.write(HEADER)
            for r in recs:
                f.write(mdfn(r) + "\n")
        print(f"wrote {jl} and {md}  ({len(recs)} episodes)")


if __name__ == "__main__":
    main()
