"""Tier-1 CROSS-SEED analysis (all discovered seeds) — implements `Plan §9`: paired
stats across seeds. Auto-discovers every v3_tier1_<grp>_seed<N>.jsonl, pools the
seeds per model group, and runs the pre-registered contrasts C1-C5 as PAIRED tests
at the (seed, instance) level:
  - McNemar exact (two-sided binomial) on SUCCESS and on CRITICAL_FAIL, separately,
    never combined into one score (Plan discipline).
  - paired bootstrap 95% CI on the pooled Δ SUCCESS% and Δ CF%.
No scipy dependency (McNemar via math.comb; bootstrap via random). seed0-only
descriptive tables live in tier1_seed0_report.py; this adds the multi-seed layer.
Read-only on results. Output -> analysis/tier1_crossseed/.

usage: python -m bench_v3.analysis.tier1_crossseed_report
"""
from __future__ import annotations
import json, glob, math, random, re
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "bench_v3" / "results"
LOGDIR = ROOT / "bench_v3"
OUT = ROOT / "bench_v3" / "analysis" / "tier1_crossseed"
LOG_ERR = re.compile(r"Traceback|RuntimeError|ERROR|Exception")

OUTCOMES = ["SUCCESS", "CRITICAL_FAIL", "OVER_CONSERVATIVE", "UNMANAGED"]
ARM_ORDER = ["single", "actor_rubric", "free_critic", "thin_critic", "bo3",
             "sc3_vote", "sc3_agg", "team_vote", "team_agg"]
ARM_LABEL = {"single": "A1 single", "actor_rubric": "A2 actor_rubric",
             "free_critic": "A3 free_critic", "thin_critic": "A4 thin_critic",
             "bo3": "A9 bo3", "sc3_vote": "A5 sc3_vote", "sc3_agg": "A6 sc3_agg",
             "team_vote": "A7 team_vote", "team_agg": "A8 team_agg"}
# Plan §4 C6 safety-discriminative classes (per-arm breakdown, NOT an A-vs-B contrast)
REBUILD_CLASSES = ["f1_rebuild_needed", "f2_chemistry_rebuild", "f3_rebalance_rebuild"]
C6_CLASSES = ["f2_instrument_recalibrate"] + REBUILD_CLASSES
# pre-registered paired contrasts (Plan §9): (label, armA, armB, question)
CONTRASTS = [
    ("C1", "actor_rubric", "single", "rubric-in-actor vs single"),
    ("C2", "free_critic", "single", "rubric-less external critic vs single"),
    ("C3a", "thin_critic", "free_critic", "rubric-in-critic vs rubric-less critic"),
    ("C3b", "thin_critic", "actor_rubric", "rubric-in-critic vs rubric-in-actor"),
    ("C4-sel-sc3", "sc3_agg", "sc3_vote", "selector: aggregator vs vote (sampling proposer)"),
    ("C4-sel-team", "team_agg", "team_vote", "selector: aggregator vs vote (persona proposer)"),
    ("C4-prop-vote", "team_vote", "sc3_vote", "proposer: personas vs sampling (vote selector)"),
    ("C4-prop-agg", "team_agg", "sc3_agg", "proposer: personas vs sampling (aggregator selector)"),
    ("C5-vs-single", "bo3", "single", "bo3 (3x compute) vs single"),
    ("C5-vs-teamagg", "bo3", "team_agg", "bo3 vs team_agg (equal-ish compute)"),
]
BOOT = 2000
RNG_SEED = 0


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]

def cls_of(r):
    return f"{r['family']}_{r['class']}"

def pct(part, n):
    return round(100 * part / n, 1) if n else 0.0

def md_table(headers, rows):
    line = lambda cells: "| " + " | ".join(str(c) for c in cells) + " |"
    return "\n".join([line(headers), "| " + " | ".join("---" for _ in headers) + " |"]
                     + [line(r) for r in rows])

def write(name, text):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(text + "\n", encoding="utf-8")
    print(f"  wrote analysis/tier1_crossseed/{name}")


# --- discovery: {group: {seed: rows}} ------------------------------------------
def discover():
    groups = defaultdict(dict)
    for mp in sorted(glob.glob(str(RESULTS / "v3_tier1_*_seed*.jsonl"))):
        if mp.endswith(".transcript.jsonl"):
            continue
        name = Path(mp).name                    # v3_tier1_<grp>_seed<N>.jsonl
        m = re.match(r"v3_tier1_(.+)_seed(\d+)\.jsonl$", name)
        grp, seed = m.group(1), int(m.group(2))
        groups[grp][seed] = load(mp)
    return groups


def scan_logs(grp):
    """Count runtime-error lines across ALL of this group's seed logs
    (seed0 -> logs_tier1_<grp>.out, seedN -> logs_tier1_<grp>_seedN.out)."""
    errs = 0
    for p in sorted(glob.glob(str(LOGDIR / f"logs_tier1_{grp}*.out"))):
        errs += sum(1 for ln in Path(p).read_text(errors="replace").splitlines() if LOG_ERR.search(ln))
    return errs


# --- stats (no scipy) ----------------------------------------------------------
def mcnemar_exact(b, c):
    """Two-sided exact McNemar (binomial) on discordant pairs b, c. Returns p."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return min(1.0, 2 * tail)

def paired_bootstrap_ci(deltas, boot=BOOT, seed=RNG_SEED):
    """95% percentile CI on mean(deltas)*100 (pp). deltas in {-1,0,1} per paired unit."""
    if not deltas:
        return (0.0, 0.0)
    rng = random.Random(seed); n = len(deltas); means = []
    for _ in range(boot):
        s = sum(deltas[rng.randrange(n)] for _ in range(n))
        means.append(100 * s / n)
    means.sort()
    lo = means[int(0.025 * boot)]; hi = means[int(0.975 * boot) - 1]
    return (round(lo, 1), round(hi, 1))


def paired_units(seeds_rows, arm, pred):
    """{(seed,instance): 1/0} for pred over the arm's episodes across all seeds."""
    d = {}
    for seed, rows in seeds_rows.items():
        for r in rows:
            if r["arm"] == arm:
                d[(seed, r["instance"])] = 1 if pred(r) else 0
    return d

IS_SUCCESS = lambda r: r["outcome"] == "SUCCESS"
IS_CF = lambda r: r["outcome"] == "CRITICAL_FAIL"


def contrast_row(seeds_rows, armA, armB, pred):
    A = paired_units(seeds_rows, armA, pred)
    B = paired_units(seeds_rows, armB, pred)
    keys = sorted(set(A) & set(B))
    a1 = sum(A[k] for k in keys); b1 = sum(B[k] for k in keys)
    b = sum(1 for k in keys if A[k] == 1 and B[k] == 0)   # A yes, B no
    c = sum(1 for k in keys if A[k] == 0 and B[k] == 1)   # A no,  B yes
    p = mcnemar_exact(b, c)
    deltas = [A[k] - B[k] for k in keys]
    lo, hi = paired_bootstrap_ci(deltas)
    n = len(keys)
    return {
        "n_pairs": n,
        "A_rate": pct(a1, n), "B_rate": pct(b1, n),
        "delta_pp": round(100 * (a1 - b1) / n, 1) if n else 0.0,
        "ci": f"[{lo:+}, {hi:+}]",
        "b_AnotB": b, "c_BnotA": c, "p": p,
        "sig": "yes" if p < 0.05 else "no",
    }


# --- reports -------------------------------------------------------------------
def data_health(groups):
    nseeds = sorted(set().union(*[set(groups[g]) for g in groups]))
    L = [f"# Tier-1 cross-seed — Data Health (Plan §1, seeds {nseeds})\n"]
    hdr = ["group", "seed", "actor", "critic", "rows", "arms(275)", "dup_keys",
           "parse_fails", "runtime_errors", "max_act", "status"]
    tr = []
    for grp in groups:
        errs = scan_logs(grp)
        for seed in sorted(groups[grp]):
            m = groups[grp][seed]
            per = Counter(r["arm"] for r in m)
            dup = sum(v - 1 for v in Counter((r["arm"], r["seed"], r["instance"]) for r in m).values() if v > 1)
            pf = sum(r.get("parse_fails", 0) for r in m)
            maxact = max((r["actions_used"] for r in m), default=0)
            armstr = f"{sum(1 for v in per.values() if v==275)}/{len(per)}"
            ok = len(m) == 2475 and dup == 0 and maxact <= 8 and armstr == "9/9"
            tr.append([grp, seed, m[0]["actor"], m[0]["critic"], len(m), armstr, dup, pf,
                       f"{errs}(grp)", maxact, "OK" if ok else "CHECK"])
    L.append(md_table(hdr, tr))
    L.append("\nruntime_errors counted per group across all seed logs.")
    write("00_data_health.md", "\n".join(L))


def outcome_by_seed(groups):
    nmin = min(len(groups[g]) for g in groups)
    if nmin >= 3:
        note = (f"Each cell = SUCC% / CF% per seed, then across-seed mean and SD "
                f"(SD shown once {nmin}+ seeds). SD is the spread *across seeds* (a "
                "stability read); significance still comes from the paired McNemar "
                "tests (02_contrasts), not from this SD. % rounded.\n")
    else:
        note = ("Each cell = SUCC% / CF% per seed, then across-seed mean. With only "
                f"{nmin} seed(s) a proper CI over seeds is degenerate — use the paired "
                "McNemar tests (02_contrasts) for significance. % rounded.\n")
    L = ["# Tier-1 cross-seed — Outcome per arm, by seed + mean (Plan §2/§9)\n", note]
    for grp in groups:
        seeds = sorted(groups[grp])
        show_sd = len(seeds) >= 3
        arms = [a for a in ARM_ORDER if any(any(r["arm"] == a for r in groups[grp][s]) for s in seeds)]
        L.append(f"\n## {grp}  (actor={groups[grp][seeds[0]][0]['actor']}, "
                 f"critic={groups[grp][seeds[0]][0]['critic']}, seeds={seeds})\n")
        hdr = ["arm"] + [f"SUCC%_s{s}" for s in seeds] + ["SUCC%_mean"] \
              + (["SUCC%_sd"] if show_sd else []) \
              + [f"CF%_s{s}" for s in seeds] + ["CF%_mean"] \
              + (["CF%_sd"] if show_sd else [])
        rows = []
        for a in arms:
            succ, cf = [], []
            for s in seeds:
                ar = [r for r in groups[grp][s] if r["arm"] == a]
                n = len(ar); oc = Counter(r["outcome"] for r in ar)
                succ.append(pct(oc["SUCCESS"], n)); cf.append(pct(oc["CRITICAL_FAIL"], n))
            row = [ARM_LABEL.get(a, a)] + succ + [round(st.mean(succ), 1)] \
                  + ([round(st.pstdev(succ), 1)] if show_sd else []) \
                  + cf + [round(st.mean(cf), 1)] \
                  + ([round(st.pstdev(cf), 1)] if show_sd else [])
            rows.append(row)
        L.append(md_table(hdr, rows))
    write("01_outcome_by_seed.md", "\n".join(L))


def contrasts(groups):
    nmin = min(len(groups[g]) for g in groups)
    L = ["# Tier-1 cross-seed — C1–C5 paired contrasts (Plan §9)\n",
         f"Paired at the (seed, instance) level, pooled over all {nmin} seeds "
         f"(so n_pairs = {nmin} x instances-in-both-arms). SUCCESS and CF tested "
         "SEPARATELY (never combined). McNemar = two-sided exact binomial on the "
         "discordant pairs (b = A-yes/B-no, c = A-no/B-yes). Δ = pooled A%−B%; "
         f"CI = paired bootstrap 95% ({BOOT} resamples, seed {RNG_SEED}). "
         "sig = McNemar p<0.05.\n"]
    for grp in groups:
        sr = groups[grp]
        present = set().union(*[{r["arm"] for r in sr[s]} for s in sr])
        L.append(f"\n## {grp}  (actor={sr[min(sr)][0]['actor']}, critic={sr[min(sr)][0]['critic']})\n")
        for metric_name, pred in [("SUCCESS", IS_SUCCESS), ("CRITICAL_FAIL", IS_CF)]:
            L.append(f"\n### {metric_name}")
            hdr = ["contrast", "A vs B", f"A {metric_name[:4]}%", "B%", "Δpp",
                   "boot95%CI", "b(A>B)", "c(B>A)", "McNemar p", "sig"]
            rows = []
            for cl, aA, aB, _q in CONTRASTS:
                if aA not in present or aB not in present:
                    continue
                r = contrast_row(sr, aA, aB, pred)
                rows.append([cl, f"{ARM_LABEL.get(aA,aA)} vs {ARM_LABEL.get(aB,aB)}",
                             r["A_rate"], r["B_rate"], f"{r['delta_pp']:+}", r["ci"],
                             r["b_AnotB"], r["c_BnotA"],
                             (f"{r['p']:.1e}" if r["p"] < 0.001 else f"{r['p']:.3f}"),
                             r["sig"]])
            L.append(md_table(hdr, rows))
        L.append("")
    L.append("\n**Reading:** a contrast is a real cross-seed effect only if McNemar sig=yes "
             "AND the bootstrap CI excludes 0. Δ is the effect size (pp). Question map:\n")
    for cl, aA, aB, q in CONTRASTS:
        L.append(f"- {cl}: {q}")
    write("02_contrasts_C1_C5_paired.md", "\n".join(L))


def c6_safety(groups):
    nmin = min(len(groups[g]) for g in groups)
    L = ["# Tier-1 cross-seed — C6 safety-discriminative classes (Plan §4), per arm\n",
         "Per-arm breakdown on the 4 safety-discriminative classes "
         "(instrument_recalibrate + the 3 rebuild classes). CF% / OVER% are the "
         f"across-seed mean over these classes (SD shown once {nmin}+ seeds); "
         "fault_cleared% is restricted to instrument_recalibrate (the only class "
         "where a meter fault can be truly cleared); needless/ep is the mean "
         "needless-intervention count. Plan §4 C6 question: does the arm reduce "
         "dangerous actions, or just hand off more conservatively? This is a per-arm "
         "descriptive table (like seed0's C6), NOT an A-vs-B paired test — read it "
         "next to the C1-C5 contrasts (02). % rounded.\n"]
    for grp in groups:
        seeds = sorted(groups[grp])
        show_sd = len(seeds) >= 3
        arms = [a for a in ARM_ORDER if any(any(r["arm"] == a for r in groups[grp][s]) for s in seeds)]
        L.append(f"\n## {grp}  (actor={groups[grp][seeds[0]][0]['actor']}, "
                 f"critic={groups[grp][seeds[0]][0]['critic']}, seeds={seeds})\n")
        L.append("classes = instrument_recalibrate + {f1_rebuild_needed, "
                 "f2_chemistry_rebuild, f3_rebalance_rebuild}\n")
        hdr = ["arm", "CF%_mean"] + (["CF%_sd"] if show_sd else []) \
              + ["OVER%_mean"] + (["OVER%_sd"] if show_sd else []) \
              + ["fault_cleared(instr)%", "needless/ep", "n/seed"]
        rows = []
        for a in arms:
            cf_s, ov_s, fc_s, nd_s, n_s = [], [], [], [], []
            for s in seeds:
                ar = [r for r in groups[grp][s] if r["arm"] == a and cls_of(r) in C6_CLASSES]
                n = len(ar); oc = Counter(r["outcome"] for r in ar)
                cf_s.append(pct(oc["CRITICAL_FAIL"], n)); ov_s.append(pct(oc["OVER_CONSERVATIVE"], n))
                appl = [r for r in ar if r.get("fault_cleared") is not None]
                fc_s.append(pct(sum(1 for r in appl if r["fault_cleared"]), len(appl)))
                nd_s.append(round(sum(r.get("needless", 0) for r in ar) / n, 2) if n else 0.0)
                n_s.append(n)
            row = [ARM_LABEL.get(a, a), round(st.mean(cf_s), 1)] \
                  + ([round(st.pstdev(cf_s), 1)] if show_sd else []) \
                  + [round(st.mean(ov_s), 1)] \
                  + ([round(st.pstdev(ov_s), 1)] if show_sd else []) \
                  + [round(st.mean(fc_s), 1), round(st.mean(nd_s), 2), n_s[0]]
            rows.append(row)
        L.append(md_table(hdr, rows))
    L.append("\n**Reading:** high fault_cleared% on instrument_recalibrate = actually "
             "fixed the meter (good); high OVER% or CF% on rebuild classes = either "
             "over-conservative handoff or dangerous wrong action. Compare an arm's "
             "CF% here against its handoff behavior to tell 'safer' from 'just more "
             "conservative'.")
    write("03_C6_safety_by_class.md", "\n".join(L))


def readme(groups):
    allseeds = sorted(set().union(*[set(groups[g]) for g in groups]))
    nmin = min(len(groups[g]) for g in groups)
    sd_note = " + SD" if nmin >= 3 else ""
    tail = ("\nNote: with 3+ seeds the paired McNemar/bootstrap (pooled over "
            "(seed,instance)) stays the significance tool; the per-seed SD in "
            "01 is a stability read, not a test. No scipy dependency."
            if nmin >= 3 else
            "\nNote: only 2 seeds — CI *across seeds* is degenerate; significance comes "
            "from the paired test pooled over (seed,instance). No scipy dependency.")
    L = [f"# Tier-1 cross-seed analysis (seeds {allseeds}) — index\n",
         "Generated by `bench_v3/analysis/tier1_crossseed_report.py` (read-only). "
         "Adds the multi-seed layer on top of the seed0-only descriptive tables "
         "(`../tier1_seed0/`). Implements Plan §9: paired McNemar + bootstrap, "
         "SUCCESS and CF reported separately, no combined score.\n",
         "| file | content |",
         "| --- | --- |",
         "| 00_data_health.md | all seeds x both groups: rows/dup/parse/errors |",
         f"| 01_outcome_by_seed.md | per-arm SUCC%/CF% by seed + across-seed mean{sd_note} |",
         "| 02_contrasts_C1_C5_paired.md | paired McNemar (exact) + bootstrap CI, C1–C5 |",
         "| 03_C6_safety_by_class.md | Plan §4 C6: per-arm CF%/OVER%/fault_cleared/needless on safety-discriminative classes |",
         "\nGroups: " + ", ".join(f"{g} (seeds {sorted(groups[g])})" for g in groups),
         tail]
    write("README.md", "\n".join(L))


def main():
    groups = discover()
    print("cross-seed groups:", {g: sorted(groups[g]) for g in groups})
    data_health(groups)
    outcome_by_seed(groups)
    contrasts(groups)
    c6_safety(groups)
    readme(groups)
    print("done ->", OUT)


if __name__ == "__main__":
    main()
