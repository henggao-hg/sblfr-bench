"""Tier-1 seed0 analysis driver — implements `Plan_Important/Tier1结果分析计划_v1.md`
STRICTLY. seed0 only (weak_seed0 + strong_seed0). Read-only on results; emits markdown
tables to `analysis/tier1_seed0/`. No new metrics beyond the Plan; JSD/action-profile are
mechanism-only. Data paths / arms / classes are discovered from the files; only the
*display order* (which the Plan fixes) is a constant.

usage: python -m bench_v3.analysis.tier1_seed0_report
"""
from __future__ import annotations
import json, glob, statistics as st
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # .../sblfr-chem
import sys; sys.path.insert(0, str(ROOT))
from bench_v3.scoring import action_profile as ap     # reuse GROUP/GROUPS/jsd/...

RESULTS = ROOT / "bench_v3" / "results"
LOGDIR = ROOT / "bench_v3"
OUT = ROOT / "bench_v3" / "analysis" / "tier1_seed0"
import re
LOG_ERR = re.compile(r"Traceback|RuntimeError|ERROR|Exception")

# --- Plan-fixed display order (membership still comes from the data) -------------
OUTCOMES = ["SUCCESS", "CRITICAL_FAIL", "OVER_CONSERVATIVE", "UNMANAGED"]
OC_SHORT = {"SUCCESS": "SUCC%", "CRITICAL_FAIL": "CF%",
            "OVER_CONSERVATIVE": "OVER%", "UNMANAGED": "UNMA%"}
ARM_ORDER = ["single", "actor_rubric", "free_critic", "thin_critic", "bo3",
             "sc3_vote", "sc3_agg", "team_vote", "team_agg"]            # plan §2 display order
ARM_LABEL = {"single": "A1 single", "actor_rubric": "A2 actor_rubric",
             "free_critic": "A3 free_critic", "thin_critic": "A4 thin_critic",
             "bo3": "A9 bo3", "sc3_vote": "A5 sc3_vote", "sc3_agg": "A6 sc3_agg",
             "team_vote": "A7 team_vote", "team_agg": "A8 team_agg"}
CLASS_ORDER = ["f1_no_fault", "f1_top_up_feasible", "f1_dilute_feasible", "f1_rebuild_needed",
               "f2_no_fault", "f2_instrument_recalibrate", "f2_chemistry_recoverable",
               "f2_chemistry_rebuild", "f3_no_fault", "f3_rebalance_feasible",
               "f3_rebalance_rebuild"]
REBUILD_CLASSES = ["f1_rebuild_needed", "f2_chemistry_rebuild", "f3_rebalance_rebuild"]
C6_CLASSES = ["f2_instrument_recalibrate"] + REBUILD_CLASSES        # plan §C6
CF_REASONS = ["a_accept_out_of_tol", "c_quarantine_accurate", "d_discard_in_tol", "e_broke_good"]


# --- io / helpers ---------------------------------------------------------------
def load(path):
    rows = []
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l:
                rows.append(json.loads(l))
    return rows

def cls_of(r):                      # full class id = family_class (matches CLASS_ORDER)
    return f"{r['family']}_{r['class']}"

def pct(part, n):
    return round(100 * part / n) if n else 0

def pct1(part, n):
    return round(100 * part / n, 1) if n else 0.0

def mean(xs):
    return round(st.mean(xs), 1) if xs else 0.0

def ordered(found, order):          # keep Plan order, append any extras seen in data
    out = [x for x in order if x in found]
    out += [x for x in found if x not in order]
    return out

def md_table(headers, rows):
    line = lambda cells: "| " + " | ".join(str(c) for c in cells) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    return "\n".join([line(headers), sep] + [line(r) for r in rows])

def write(name, text):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(text + "\n", encoding="utf-8")
    print(f"  wrote analysis/tier1_seed0/{name}")


# --- discovery ------------------------------------------------------------------
def discover():
    """Return [(group_label, metrics_path, transcript_path), ...] for seed0 only."""
    groups = []
    for mp in sorted(glob.glob(str(RESULTS / "v3_tier1_*_seed0.jsonl"))):
        if mp.endswith(".transcript.jsonl"):
            continue
        name = Path(mp).name                       # v3_tier1_<grp>_seed0.jsonl
        grp = name[len("v3_tier1_"):-len("_seed0.jsonl")]
        tp = mp[:-len(".jsonl")] + ".transcript.jsonl"
        groups.append((grp, mp, tp if Path(tp).exists() else None))
    return groups


# --- §1 data health -------------------------------------------------------------
def scan_logs(grp):
    """Find seed0 run logs for this group and count runtime-error lines (Plan §1)."""
    cands = [LOGDIR / f"logs_tier1_{grp}.out", LOGDIR / f"logs_tier1_{grp}_seed0.out"]
    found = [p for p in cands if p.exists()]
    if not found:
        return "no log found", None
    errs, samples = 0, []
    for p in found:
        for ln in p.read_text(errors="replace").splitlines():
            if LOG_ERR.search(ln):
                errs += 1
                if len(samples) < 2:
                    samples.append(ln.strip()[:120])
    tag = ", ".join(p.name for p in found)
    return (f"{errs} ({tag})", samples if errs else None)


def data_health(groups):
    lines = ["# Tier-1 seed0 — Data Health (Plan §1)\n",
             "seed0 only. weak_seed1/strong_seed1 excluded by design.\n"]
    hdr = ["group", "actor", "critic", "seed", "metrics_rows", "transcript_rows",
           "arms_complete(275)", "dup_keys", "key_match", "parse_fails",
           "runtime_errors", "max_actions_used", "status"]
    trows = []
    health = {}
    err_samples = {}
    for grp, mp, tp in groups:
        m = load(mp)
        t = load(tp) if tp else []
        per_arm = Counter(r["arm"] for r in m)
        arms_ok = all(v == 275 for v in per_arm.values()) and len(per_arm) >= 1
        arms_str = f"{sum(1 for v in per_arm.values() if v==275)}/{len(per_arm)}"
        # duplicate (arm,seed,instance) keys in metrics and transcript
        mkc = Counter((r["arm"], r["seed"], r["instance"]) for r in m)
        tkc = Counter((r["arm"], r["seed"], r["instance"]) for r in t)
        dup = sum(c - 1 for c in mkc.values() if c > 1) + sum(c - 1 for c in tkc.values() if c > 1)
        # key-level match on arm,seed,instance -> outcome,actions_used
        mismatch = 0
        if t:
            mk = {(r["arm"], r["seed"], r["instance"]): (r["outcome"], r["actions_used"]) for r in m}
            for r in t:
                k = (r["arm"], r["seed"], r["instance"])
                if k not in mk or mk[k] != (r["outcome"], r["actions_used"]):
                    mismatch += 1
        pf = sum(r.get("parse_fails", 0) for r in m)
        maxact = max((r["actions_used"] for r in m), default=0)
        log_str, samples = scan_logs(grp)
        if samples:
            err_samples[grp] = samples
        actor = m[0]["actor"]; critic = m[0]["critic"]; seed = m[0]["seed"]
        log_clean = log_str.startswith("0 ")
        ok = (len(m) == 2475 and (not t or len(t) == 2475) and arms_ok and dup == 0
              and mismatch == 0 and maxact <= 8 and log_clean)
        trows.append([grp, actor, critic, seed, len(m), len(t) if t else "—",
                      arms_str, dup, f"{mismatch} mismatch", pf, log_str, maxact,
                      "OK" if ok else "CHECK"])
        health[grp] = {"rows": m, "trows": t, "actor": actor, "critic": critic, "ok": ok}
    lines.append(md_table(hdr, trows))
    lines.append("\n- key_match = transcript vs metrics agreement on "
                 "(arm,seed,instance)->(outcome,actions_used). Key-level (order-insensitive); "
                 "duplicate keys are caught separately by dup_keys.")
    lines.append("- runtime_errors = count of lines matching Traceback/RuntimeError/ERROR/Exception "
                 "in the seed0 run log(s); 'no log found' if the log file is absent.")
    if err_samples:
        lines.append("\n### runtime-error samples")
        for grp, ss in err_samples.items():
            for s in ss:
                lines.append(f"- [{grp}] `{s}`")
    write("00_data_health.md", "\n".join(lines))
    return health


# --- §2 nine-arm outcome table --------------------------------------------------
def outcome_block(rows, arms):
    hdr = ["arm", "SUCC%", "CF%", "OVER%", "UNMA%", "n", "parse_fails", "calls/ep", "tokens/ep"]
    out = []
    for a in arms:
        ar = [r for r in rows if r["arm"] == a]
        n = len(ar); oc = Counter(r["outcome"] for r in ar)
        calls = mean([r["actor_calls"] + r["critic_calls"] for r in ar])
        toks = mean([r["actor_pt"] + r["actor_ct"] + r["critic_pt"] + r["critic_ct"] for r in ar])
        pf = sum(r.get("parse_fails", 0) for r in ar)
        out.append([ARM_LABEL.get(a, a), pct(oc["SUCCESS"], n), pct(oc["CRITICAL_FAIL"], n),
                    pct(oc["OVER_CONSERVATIVE"], n), pct(oc["UNMANAGED"], n), n, pf, calls, toks])
    return md_table(hdr, out)

def nine_arm(health):
    lines = ["# Tier-1 seed0 — 9-arm Outcome Tables (Plan §2)\n",
             "Outcomes are the 4-tier ladder only. % rounded.\n"]
    for grp, h in health.items():
        arms = ordered(set(r["arm"] for r in h["rows"]), ARM_ORDER)
        lines.append(f"## {grp}  (actor={h['actor']}, critic={h['critic']})\n")
        lines.append(outcome_block(h["rows"], arms))
        lines.append("")
    write("01_outcome_9arm.md", "\n".join(lines))


# --- §3 by-class outcome --------------------------------------------------------
def by_class(health):
    lines = ["# Tier-1 seed0 — Outcome by Class (Plan §3)\n",
             "Per arm, split by class. % rounded.\n"]
    for grp, h in health.items():
        rows = h["rows"]
        arms = ordered(set(r["arm"] for r in rows), ARM_ORDER)
        classes = ordered(set(cls_of(r) for r in rows), CLASS_ORDER)
        lines.append(f"## {grp}  (actor={h['actor']}, critic={h['critic']})\n")
        hdr = ["arm", "class", "SUCC%", "CF%", "OVER%", "UNMA%", "n"]
        trows = []
        for a in arms:
            for c in classes:
                ar = [r for r in rows if r["arm"] == a and cls_of(r) == c]
                n = len(ar); oc = Counter(r["outcome"] for r in ar)
                trows.append([ARM_LABEL.get(a, a), c, pct(oc["SUCCESS"], n),
                              pct(oc["CRITICAL_FAIL"], n), pct(oc["OVER_CONSERVATIVE"], n),
                              pct(oc["UNMANAGED"], n), n])
        lines.append(md_table(hdr, trows))
        lines.append("")
    write("02_outcome_by_class.md", "\n".join(lines))


# --- metric helpers for contrasts ----------------------------------------------
def arm_rows(rows, a):
    return [r for r in rows if r["arm"] == a]

def succ_cf(rows, a, classes=None):
    ar = arm_rows(rows, a)
    if classes is not None:
        ar = [r for r in ar if cls_of(r) in classes]
    n = len(ar); oc = Counter(r["outcome"] for r in ar)
    return n, pct(oc["SUCCESS"], n), pct(oc["CRITICAL_FAIL"], n), pct(oc["OVER_CONSERVATIVE"], n)

def fault_cleared_rate(rows, a, classes):
    ar = [r for r in arm_rows(rows, a) if cls_of(r) in classes]
    appl = [r for r in ar if r.get("fault_cleared") is not None]
    cleared = sum(1 for r in appl if r["fault_cleared"])
    return f"{pct(cleared, len(appl))}% ({cleared}/{len(appl)})" if appl else "n.a."

def needless_per_ep(rows, a, classes=None):
    ar = arm_rows(rows, a)
    if classes is not None:
        ar = [r for r in ar if cls_of(r) in classes]
    return round(sum(r.get("needless", 0) for r in ar) / len(ar), 2) if ar else 0.0

def calls_tokens(rows, a):
    ar = arm_rows(rows, a)
    calls = mean([r["actor_calls"] + r["critic_calls"] for r in ar])
    toks = mean([r["actor_pt"] + r["actor_ct"] + r["critic_pt"] + r["critic_ct"] for r in ar])
    return calls, toks


# --- §4 C1–C6 contrasts ---------------------------------------------------------
def contrasts(health):
    L = ["# Tier-1 seed0 — C1–C6 Pre-registered Contrasts (Plan §4)\n",
         "Paired: same instance/seed/model-group. seed0 = **descriptive only** "
         "(no CI / significance until multi-seed). All % rounded.\n"]
    for grp, h in health.items():
        rows = h["rows"]
        present = set(r["arm"] for r in rows)
        L.append(f"\n## {grp}  (actor={h['actor']}, critic={h['critic']})\n")

        def line(a):
            n, s, cf, ov = succ_cf(rows, a)
            return [ARM_LABEL.get(a, a), s, cf, ov, n]

        # C1 A2 vs A1
        if {"single", "actor_rubric"} <= present:
            L.append("### C1 — actor_rubric (A2) vs single (A1): does rubric-in-actor help?")
            L.append(md_table(["arm", "SUCC%", "CF%", "OVER%", "n"],
                              [line("single"), line("actor_rubric")]))
            _, s1, cf1, _ = succ_cf(rows, "single"); _, s2, cf2, _ = succ_cf(rows, "actor_rubric")
            L.append(f"Δ SUCC = {s2-s1:+d} pp,  Δ CF = {cf2-cf1:+d} pp.  (class-level: see 02_outcome_by_class.md)\n")

        # C2 A3 vs A1
        if {"single", "free_critic"} <= present:
            L.append("### C2 — free_critic (A3) vs single (A1): value of a rubric-less external critic?")
            tbl = []
            for a in ["single", "free_critic"]:
                n, s, cf, ov = succ_cf(rows, a); c, t = calls_tokens(rows, a)
                tbl.append([ARM_LABEL[a], s, cf, ov, c, t, n])
            L.append(md_table(["arm", "SUCC%", "CF%", "OVER%", "calls/ep", "tokens/ep", "n"], tbl))
            _, s1, cf1, _ = succ_cf(rows, "single"); _, s3, cf3, _ = succ_cf(rows, "free_critic")
            L.append(f"Δ SUCC = {s3-s1:+d} pp,  Δ CF = {cf3-cf1:+d} pp.\n")

        # C3 A4 vs A3, A4 vs A2
        if "thin_critic" in present:
            L.append("### C3 — thin_critic (A4) vs free_critic (A3) and vs actor_rubric (A2): where does the rubric work best?")
            tbl = []
            for a in ["actor_rubric", "free_critic", "thin_critic"]:
                if a not in present:
                    continue
                n, s, cf, ov = succ_cf(rows, a)
                fc = fault_cleared_rate(rows, a, ["f2_instrument_recalibrate"])
                tbl.append([ARM_LABEL[a], s, cf, ov, fc, needless_per_ep(rows, a), n])
            L.append(md_table(["arm", "SUCC%", "CF%", "OVER%",
                               "fault_cleared(instr)", "needless/ep", "n"], tbl))
            L.append("")

        # C4 2x2
        quad = ["sc3_vote", "sc3_agg", "team_vote", "team_agg"]
        if all(a in present for a in quad):
            L.append("### C4 — 2×2 (proposer: sampling vs personas) × (selector: vote vs aggregator)")
            tbl = []
            for a in quad:
                n, s, cf, ov = succ_cf(rows, a)
                _, sr, cfr, ovr = succ_cf(rows, a, REBUILD_CLASSES)
                tbl.append([ARM_LABEL[a], s, cf, ov, sr, cfr, ovr, n])
            L.append(md_table(["arm", "SUCC%", "CF%", "OVER%",
                               "rebuild SUCC%", "rebuild CF%", "rebuild OVER%", "n"], tbl))
            sv = succ_cf(rows, "sc3_vote")[1]; sa = succ_cf(rows, "sc3_agg")[1]
            tv = succ_cf(rows, "team_vote")[1]; ta = succ_cf(rows, "team_agg")[1]
            L.append(f"\nSUCC% main effects — selector(agg−vote): sc3 {sa-sv:+d}, team {ta-tv:+d}; "
                     f"proposer(team−sc3): vote {tv-sv:+d}, agg {ta-sa:+d}.")
            L.append("(rebuild SUCC/CF/OVER = aggregate over f1_rebuild_needed, f2_chemistry_rebuild, f3_rebalance_rebuild)\n")

        # C5 bo3
        if "bo3" in present:
            L.append("### C5 — bo3 (A9, ~3× compute) vs single (A1) and vs 2×2")
            tbl = []
            for a in ["single", "bo3"] + [q for q in quad if q in present]:
                n, s, cf, ov = succ_cf(rows, a); c, t = calls_tokens(rows, a)
                tbl.append([ARM_LABEL[a], s, cf, ov, c, t, n])
            L.append(md_table(["arm", "SUCC%", "CF%", "OVER%", "calls/ep", "tokens/ep", "n"], tbl))
            L.append("(bo3 is a compute control, not a low-cost improvement.)\n")

        # C6 safety-discriminative classes
        L.append("### C6 — safety-discriminative classes (per arm): CF%, OVER%, fault_cleared, needless")
        arms = ordered(present, ARM_ORDER)
        tbl = []
        for a in arms:
            n, s, cf, ov = succ_cf(rows, a, C6_CLASSES)
            fc = fault_cleared_rate(rows, a, ["f2_instrument_recalibrate"])
            tbl.append([ARM_LABEL.get(a, a), cf, ov, fc, needless_per_ep(rows, a, C6_CLASSES), n])
        L.append(md_table(["arm", "CF%", "OVER%", "fault_cleared(instr)", "needless/ep", "n"], tbl))
        L.append("(classes = instrument_recalibrate + the three rebuild classes)\n")
    write("03_contrasts_C1_C6.md", "\n".join(L))


# --- §5 secondary + §6 cost -----------------------------------------------------
def cost_and_secondary(health):
    L = ["# Tier-1 seed0 — Cost & Secondary Safety Metrics (Plan §5–§6)\n"]
    for grp, h in health.items():
        rows = h["rows"]
        arms = ordered(set(r["arm"] for r in rows), ARM_ORDER)
        L.append(f"\n## {grp}  (actor={h['actor']}, critic={h['critic']})\n")
        # cost (§6)
        L.append("### Cost per episode (§6)")
        hdr = ["arm", "actor_calls/ep", "critic_calls/ep", "total_calls/ep",
               "actor_tok/ep", "critic_tok/ep", "total_tok/ep"]
        tbl = []
        for a in arms:
            ar = arm_rows(rows, a)
            ac = mean([r["actor_calls"] for r in ar]); cc = mean([r["critic_calls"] for r in ar])
            at = mean([r["actor_pt"] + r["actor_ct"] for r in ar])
            ct = mean([r["critic_pt"] + r["critic_ct"] for r in ar])
            tbl.append([ARM_LABEL.get(a, a), ac, cc, round(ac+cc, 1), at, ct, round(at+ct, 1)])
        L.append(md_table(hdr, tbl))
        # needless by class (§5)
        L.append("\n### needless_interventions (§5): total / per-ep, by class")
        classes = ordered(set(cls_of(r) for r in rows), CLASS_ORDER)
        hdr2 = ["arm"] + [c.replace("f1_", "1·").replace("f2_", "2·").replace("f3_", "3·") for c in classes] + ["all/ep"]
        tbl2 = []
        for a in arms:
            cells = [ARM_LABEL.get(a, a)]
            for c in classes:
                ar = [r for r in arm_rows(rows, a) if cls_of(r) == c]
                cells.append(sum(r.get("needless", 0) for r in ar))
            cells.append(needless_per_ep(rows, a))
            tbl2.append(cells)
        L.append(md_table(hdr2, tbl2))
        # cf_reason breakdown (§5)
        L.append("\n### CRITICAL_FAIL by cf_reason (§5)")
        hdr3 = ["arm", "CF total"] + CF_REASONS
        tbl3 = []
        for a in arms:
            ar = arm_rows(rows, a)
            cfr = Counter(r["cf_reason"] for r in ar if r["outcome"] == "CRITICAL_FAIL")
            tbl3.append([ARM_LABEL.get(a, a), sum(cfr.values())] + [cfr.get(x, 0) for x in CF_REASONS])
        L.append(md_table(hdr3, tbl3))
    write("04_cost_secondary.md", "\n".join(L))


# --- §7 action profile / JSD ----------------------------------------------------
def action_profile(health):
    L = ["# Tier-1 seed0 — Action Profile / JSD (Plan §7, MECHANISM ONLY)\n",
         "Not a success metric. JSD vs single only meaningful ABOVE the single self-split "
         "noise floor.\n"]
    for grp, h in health.items():
        rows = h["rows"]
        arms = ordered(set(r["arm"] for r in rows), ARM_ORDER)
        single = arm_rows(rows, "single")
        floor = ap.noise_floor(single, seed=0)
        single_share = ap.group_share(single)
        L.append(f"\n## {grp}  (actor={h['actor']}, critic={h['critic']})  "
                 f"— single self-split noise floor JSD = {floor}\n")
        # group_share
        L.append("### group_share (step-weighted, 6 groups)")
        L.append(md_table(["arm"] + ap.GROUPS,
                          [[ARM_LABEL.get(a, a)] + [round(ap.group_share(arm_rows(rows, a))[g], 3) for g in ap.GROUPS]
                           for a in arms]))
        # incidence
        L.append("\n### incidence (% episodes doing each action ≥once)")
        inc_keys = ["std_check%", "recal%", "discard%", "inplace%", "handoff%", "accept%"]
        L.append(md_table(["arm"] + inc_keys,
                          [[ARM_LABEL.get(a, a)] + [ap.incidence(arm_rows(rows, a))[k] for k in inc_keys]
                           for a in arms]))
        # JSD vs single (overall)
        L.append("\n### JSD vs single (overall)")
        L.append(md_table(["arm", "JSD vs single", "above floor?"],
                          [[ARM_LABEL.get(a, a),
                            ap.jsd(ap.group_share(arm_rows(rows, a)), single_share),
                            "yes" if floor is not None and ap.jsd(ap.group_share(arm_rows(rows, a)), single_share) > floor else "no"]
                           for a in arms if a != "single"]))
        # JSD by class (plan §7 example), focus on discriminative classes
        L.append("\n### JSD vs single by class (discriminative classes) + behavior incidences")
        hdr = ["arm", "class", "JSD vs single", "discard%", "handoff%", "std_check%", "recal%"]
        tbl = []
        for a in arms:
            if a == "single":
                continue
            for c in C6_CLASSES:
                sc = [r for r in single if cls_of(r) == c]
                ac = [r for r in arm_rows(rows, a) if cls_of(r) == c]
                if not ac or not sc:
                    continue
                inc = ap.incidence(ac)
                tbl.append([ARM_LABEL.get(a, a), c, ap.jsd(ap.group_share(ac), ap.group_share(sc)),
                            inc["discard%"], inc["handoff%"], inc["std_check%"], inc["recal%"]])
        L.append(md_table(hdr, tbl))
    write("05_action_profile_jsd.md", "\n".join(L))

def motifs(health):
    L = ["# Tier-1 seed0 — Top trace motifs by (arm, class) (Plan §7)\n",
         "Abbrev: Mv measure_conc · Mvol measure_vol · Msv measure_stock_vol · Mstk measure_stock_conc · "
         "Mstd measure_standard · R recalibrate · T transfer · D dilute · X discard · Q quarantine · "
         "A accept · H handoff. Top-3 motifs per cell (count).\n"]
    for grp, h in health.items():
        rows = h["rows"]
        arms = ordered(set(r["arm"] for r in rows), ARM_ORDER)
        classes = ordered(set(cls_of(r) for r in rows), CLASS_ORDER)
        L.append(f"\n## {grp}  (actor={h['actor']}, critic={h['critic']})\n")
        for c in classes:
            L.append(f"\n**{c}**")
            for a in arms:
                ar = [r for r in arm_rows(rows, a) if cls_of(r) == c]
                cc = Counter(ap.motif(r) for r in ar).most_common(3)
                top = "  |  ".join(f"`{m or '∅'}`×{n}" for m, n in cc)
                L.append(f"- {ARM_LABEL.get(a, a)}: {top}")
    write("05b_motifs.md", "\n".join(L))


# --- §8 case audit index --------------------------------------------------------
def case_audit_index(health):
    # transcript line locators per group
    L = ["# Tier-1 seed0 — Case Audit Index (Plan §8)\n",
         "Curated candidate episodes for manual audit (max 3 per finding). "
         "Action sequence shown as motif; interpretation is left to the manual write-up "
         "(Plan §10: anecdotes only explain patterns already in the aggregate).\n"]

    def locators(grp):
        _, mp, tp = next(g for g in DISCOVERED if g[0] == grp)
        loc = {}
        if tp:
            with open(tp) as f:
                for i, l in enumerate(f, 1):
                    if not l.strip():
                        continue
                    r = json.loads(l)
                    loc[(r["arm"], r["instance"])] = i
        return Path(tp).name if tp else "—", loc

    def pick(grp, pred, k=3):
        rows = [r for r in health[grp]["rows"] if pred(r)]
        return rows[:k]

    def render(title, want):
        L.append(f"\n## {title}")
        if not want:
            L.append("_(no matching episodes / group absent)_")
            return
        for grp, rows in want:
            fname, loc = locators(grp)
            hdr = ["model", "arm", "instance", "outcome", "cf_reason", "motif", "transcript"]
            tbl = []
            for r in rows:
                ln = loc.get((r["arm"], r["instance"]))
                tbl.append([grp, ARM_LABEL.get(r["arm"], r["arm"]), r["instance"], r["outcome"],
                            r.get("cf_reason") or "—", "`" + ap.motif(r) + "`",
                            f"{fname}:L{ln}" if ln else "—"])
            L.append(md_table(hdr, tbl))

    grps = list(health.keys())
    strong = next((g for g in grps if "strong" in g), None)
    weak = next((g for g in grps if "weak" in g), None)

    render("strong team_agg OVER_CONSERVATIVE (aggregator biased to handoff?)",
           [(strong, pick(strong, lambda r: r["arm"] == "team_agg" and r["outcome"] == "OVER_CONSERVATIVE"))]
           if strong else [])
    render("weak CRITICAL_FAIL e_broke_good (corrective broke a good batch?)",
           [(weak, pick(weak, lambda r: r["outcome"] == "CRITICAL_FAIL" and r.get("cf_reason") == "e_broke_good"))]
           if weak else [])
    render("weak thin_critic — typical SUCCESS and non-SUCCESS",
           [(weak, pick(weak, lambda r: r["arm"] == "thin_critic" and r["outcome"] == "SUCCESS", 2)
                  + pick(weak, lambda r: r["arm"] == "thin_critic" and r["outcome"] != "SUCCESS", 1))]
           if weak else [])
    render("bo3 typical SUCCESS (one of 3 runs went right?)",
           [(strong, pick(strong, lambda r: r["arm"] == "bo3" and r["outcome"] == "SUCCESS"))]
           if strong else [])
    write("06_case_audit_index.md", "\n".join(L))


def index_readme(health):
    L = ["# Tier-1 seed0 analysis — index\n",
         "Generated by `bench_v3/analysis/tier1_seed0_report.py` (read-only on results). "
         "Strictly follows `Plan_Important/Tier1结果分析计划_v1.md`. seed0 only.\n",
         "| file | Plan section | content |",
         "| --- | --- | --- |",
         "| 00_data_health.md | §1 | completeness / row-match / parse / errors |",
         "| 01_outcome_9arm.md | §2 | 9-arm 4-tier outcome table per model group |",
         "| 02_outcome_by_class.md | §3 | outcome split by class |",
         "| 03_contrasts_C1_C6.md | §4 | C1–C6 pre-registered contrasts (descriptive) |",
         "| 04_cost_secondary.md | §5–§6 | cost/ep, needless by class, cf_reason |",
         "| 05_action_profile_jsd.md | §7 | group_share, incidence, JSD vs single (mechanism) |",
         "| 05b_motifs.md | §7 | top trace motifs per (arm,class) |",
         "| 06_case_audit_index.md | §8 | curated candidate episodes for manual audit |",
         "\nGroups analyzed: " + ", ".join(f"{g} (actor={h['actor']}, critic={h['critic']})"
                                            for g, h in health.items()),
         "\n**seed0 = descriptive only.** No CI / significance until multi-seed (Plan §9). "
         "JSD/action-profile are mechanism, never success (Plan §7/§10)."]
    write("README.md", "\n".join(L))


DISCOVERED = []
def main():
    global DISCOVERED
    DISCOVERED = discover()
    print("discovered seed0 groups:", [g[0] for g in DISCOVERED])
    health = data_health(DISCOVERED)
    nine_arm(health)
    by_class(health)
    contrasts(health)
    cost_and_secondary(health)
    action_profile(health)
    motifs(health)
    case_audit_index(health)
    index_readme(health)
    print("done ->", OUT)


if __name__ == "__main__":
    main()
