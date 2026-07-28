"""Augment decay_curve_all_seeds.csv with per-(arm,k,seed) counts (hits, n).

SINGLE-SOURCE discipline: the existing `p` column is the source of truth. This script
recomputes p from counts (hits/n) using the pinned metric and REQUIRES it to reproduce
the existing p in every non-empty cell (regression gate). If any cell disagrees it ABORTS
and prints the discrepancies -- it never silently overwrites. On success it rewrites the
CSV preserving `p` verbatim and appending `hits`, `n`.

Metric (pinned): first committed step whose TRUE state is in tolerance (step with
tia == True), over the four decay arms {actor_rubric, free_critic, thin_critic, team_agg},
ALL classes, weak model. hits = episodes first-in-tol at step k that ended SUCCESS;
n = episodes first-in-tol at step k. p = round(100*hits/n).

Run (NixOS loader path not needed; pure stdlib):
  python -m bench_v3.analysis.decay_counts
"""
from __future__ import annotations
import csv, json, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "bench_v3" / "results"
CSVP = ROOT / "bench_v3" / "analysis" / "tier1_crossseed" / "decay_curve_all_seeds.csv"
ARMS = ["actor_rubric", "free_critic", "thin_critic", "team_agg"]
SEEDS = [0, 1, 2]


def first_in_tol_step(steps):
    """First committed step index whose true state is in tolerance (tia True), else None."""
    for st in steps:
        if st.get("committed") and st.get("tia") is True:
            return st["step"]
    return None


def compute_counts():
    counts = collections.defaultdict(lambda: [0, 0])   # (arm,k,seed) -> [hits, n]
    for seed in SEEDS:
        for ln in open(RESULTS / f"v3_tier1_weak_seed{seed}.transcript.jsonl"):
            d = json.loads(ln)
            if d["arm"] not in ARMS:
                continue
            k = first_in_tol_step(d["steps"])
            if k is None:
                continue
            cell = counts[(d["arm"], k, seed)]
            cell[1] += 1
            if d["outcome"] == "SUCCESS":
                cell[0] += 1
    return counts


def main():
    counts = compute_counts()
    rows = list(csv.DictReader(open(CSVP)))
    out_rows, mismatches = [], []
    for r in rows:
        arm, k, seed = r["arm"], int(r["k"]), int(r["seed"])
        h, n = counts.get((arm, k, seed), [0, 0])
        p_new = round(100 * h / n) if n > 0 else None
        old = r["p"]
        old_norm = None if old in ("", "-") else int(float(old))
        if p_new != old_norm:
            mismatches.append((arm, k, seed, f"{h}/{n}={p_new}", old))
        out_rows.append({"arm": arm, "k": k, "seed": seed, "p": old,   # preserve p verbatim
                         "hits": h if n > 0 else "-", "n": n})
    if mismatches:
        print(f"ABORT: {len(mismatches)} cell(s) disagree with existing p (not overwriting):")
        for arm, k, seed, mine, old in mismatches:
            print(f"  {arm} k={k} seed={seed}: counts->{mine}  vs old p={old}")
        return
    with open(CSVP, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["arm", "k", "seed", "p", "hits", "n"])
        w.writeheader(); w.writerows(out_rows)
    nonempty = sum(1 for r in out_rows if r["n"] > 0)
    print(f"regression gate PASSED ({nonempty} non-empty cells reproduce p exactly).")
    print(f"wrote {CSVP} with hits,n columns.")


if __name__ == "__main__":
    main()
