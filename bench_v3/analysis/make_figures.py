"""R&D chapter figures (5 required + 1 optional).

NO titles and NO interpretive/conclusion text inside the figures -- only results and
necessary markers (axes, legends, arm names, numeric value labels, k=7/k=8 structural
lines). Titles/captions are written in the paper.

Palette: soft-pastel, matched to "LLMs Get Lost in Multi-Turn Conversation" (sage green
= success, coral-red = critical-fail, amber = handoff, steel-blue = unmanaged). Layout:
clean tau-bench-like matplotlib. Craft: 3 seeds always visible (scatter, never error bars).

Data (read live):
  fig1/fig4/maintable : bench_v3/results/v3_tier1_{weak,strong}_seed{0,1,2}.jsonl
  fig2                : bench_v3/analysis/tier1_crossseed/decay_curve_all_seeds.csv
  fig3                : bench_v3/results/v3_ablation_weak_seed0.jsonl + tier1 (seed0)
  fig5/fig6           : mechanism metrics from the three-seed report (cited inline)

Run (NixOS needs the C libs on the loader path):
  LD_LIBRARY_PATH=/nix/store/cf1a53iqg6ncnygl698c4v0l8qam5a2q-gcc-14.3.0-lib/lib:\
/nix/store/f2q5ld1nipl8w1r2w8m6azhlm2varqgb-zlib-1.3.1/lib \
  python -m bench_v3.analysis.make_figures
"""
from __future__ import annotations
import csv, json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "bench_v3" / "results"
CROSS = ROOT / "bench_v3" / "analysis" / "tier1_crossseed"
OUT = ROOT / "bench_v3" / "analysis" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# ---- palette (lost-in-conversation hierarchy) ----
# PRIMARY = blue + amber families (carry the bulk: neutral tiers, series, arms, models).
# SECONDARY accents used ONLY for their semantic verdict: green = SUCCESS, coral = CRITICAL_FAIL.
C_SUCCESS = "#6BA368"; C_CF = "#D1615D"                       # verdict accents (secondary)
C_BLUE = "#4E79A7"; C_BLUE_D = "#2C4E70"; C_BLUE_L = "#8FA9C2"; C_SKY = "#7FB0D4"; C_NAVY_L = "#A9C0D6"
C_AMBER = "#E4B94F"; C_AMBER_D = "#C08A1E"; C_AMBER_L = "#F0D482"; C_BROWN = "#8A5A2B"; C_INDIGO = "#6B5B95"
C_SEED = "#2E3B4E"
C_HANDOFF = C_AMBER; C_UNMAN = C_BLUE_L
TIER_ORDER = ["SUCCESS", "HANDOFF", "UNMANAGED", "CRITICAL_FAIL"]
TIER_COLOR = {"SUCCESS": C_SUCCESS, "HANDOFF": C_HANDOFF, "UNMANAGED": C_UNMAN,
              "CRITICAL_FAIL": C_CF}
OUT2TIER = {"SUCCESS": "SUCCESS", "OVER_CONSERVATIVE": "HANDOFF",
            "UNMANAGED": "UNMANAGED", "CRITICAL_FAIL": "CRITICAL_FAIL"}

ARMS = ["single", "actor_rubric", "free_critic", "thin_critic",
        "sc3_vote", "sc3_agg", "team_vote", "team_agg", "bo3"]
ARM_DISP = {"single": "single", "actor_rubric": "actor\nrubric", "free_critic": "free\ncritic",
            "thin_critic": "thin\ncritic", "sc3_vote": "sc3\nvote", "sc3_agg": "sc3\nagg",
            "team_vote": "team\nvote", "team_agg": "team\nagg", "bo3": "bo3"}
# short readable labels (figures use these; the abbrev->arm table goes in the caption).
ARM_ID = {"single": "Single", "actor_rubric": "+Principles", "free_critic": "Critic",
          "thin_critic": "Critic+P", "sc3_vote": "SC-vote", "sc3_agg": "SC-agg",
          "team_vote": "MA-vote", "team_agg": "MA-agg", "bo3": "Best-of-3"}
ABL_ID = {"rubric_reassert": "Reassert", "single_stoprule": "Stop-rule",
          "single_personaB": "Persona-B"}
# 9-arm categorical palette: blue-family + amber-family + indigo (NO green/red -- those
# stay reserved for the SUCCESS/CF verdict accents).
ARM_COLOR = {"single": C_NAVY_L, "actor_rubric": C_BLUE, "free_critic": C_BLUE_D,
             "thin_critic": C_SKY, "sc3_vote": C_AMBER_L, "sc3_agg": C_AMBER,
             "team_vote": C_AMBER_D, "team_agg": C_BROWN, "bo3": C_INDIGO}
MODEL_ID = {"weak": "weak / Qwen2.5-32B", "strong": "strong / Qwen3.7-Max"}
SEEDS = [0, 1, 2]; N = 275

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#555555", "axes.linewidth": 0.8,
    "axes.grid": True, "grid.color": "#DDDDDD", "grid.linewidth": 0.6,
    "axes.axisbelow": True, "figure.dpi": 120,
})


def load_counts(path):
    d = defaultdict(Counter)
    for ln in open(path):
        ln = ln.strip()
        if ln:
            r = json.loads(ln); d[r["arm"]][r["outcome"]] += 1
    return d


def tier1():
    return {m: {s: load_counts(RESULTS / f"v3_tier1_{m}_seed{s}.jsonl") for s in SEEDS}
            for m in ("weak", "strong")}


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", dpi=300)
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote figures/{name}.png + .pdf")


# ============================================================ FIG 1
def fig1_main(T1):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6), sharey=True)
    for ax, model in zip(axes, ("weak", "strong")):
        x = range(len(ARMS))
        mean = {a: {t: 0.0 for t in TIER_ORDER} for a in ARMS}
        for a in ARMS:
            for s in SEEDS:
                for o, n in T1[model][s][a].items():
                    mean[a][OUT2TIER[o]] += n / len(SEEDS)
        bottom = [0.0] * len(ARMS)
        for t in TIER_ORDER:
            vals = [mean[a][t] for a in ARMS]
            ax.bar(x, vals, bottom=bottom, width=0.6, color=TIER_COLOR[t],
                   edgecolor="white", linewidth=0.5, label=t, zorder=2)
            bottom = [b + v for b, v in zip(bottom, vals)]
        for i, a in enumerate(ARMS):
            succ = [T1[model][s][a].get("SUCCESS", 0) for s in SEEDS]
            ax.scatter([i + j for j in (-0.16, 0.0, 0.16)], succ, s=16, color=C_SEED,
                       zorder=5, edgecolor="white", linewidth=0.4)
        ax.text(0.0, 1.02, MODEL_ID[model], transform=ax.transAxes, fontsize=10,
                va="bottom", ha="left", color="#333333")
        ax.set_xticks(list(x))
        ax.set_xticklabels([ARM_ID[a] for a in ARMS], fontsize=8, rotation=25, ha="right")
        ax.set_ylim(0, N); ax.set_xlim(-0.6, len(ARMS) - 0.4)
    axes[0].set_ylabel("episodes  (/ 275)")
    handles = [Patch(facecolor=TIER_COLOR[t], label=t) for t in TIER_ORDER]
    handles.append(Line2D([0], [0], marker="o", color="none", markerfacecolor=C_SEED,
                          markeredgecolor="white", markersize=5, label="per-seed SUCCESS"))
    fig.legend(handles=handles, ncol=5, loc="lower center", frameon=False,
               bbox_to_anchor=(0.5, -0.04), fontsize=9)
    save(fig, "fig1_main_outcomes")


# ============================================================ FIG 2
def fig2_decay():
    """Decay curve. SINGLE-SOURCE: consumes the neighbour's decay CSV. When it carries
    per-(arm,k,seed) counts (hits,n columns), pool hits and n across seeds -> one
    percentage per (arm,k), and size each point by the pooled n (few episodes = small dot,
    ~100 = big). Until those columns exist, render the interim per-seed-mean line (jagged)
    and print a notice -- we do NOT recompute the metric here (avoids a second source)."""
    rows = list(csv.DictReader(open(CROSS / "decay_curve_all_seeds.csv")))
    fields = set(rows[0].keys()) if rows else set()
    has_counts = {"hits", "n"} <= fields
    lines = {"actor_rubric": (ARM_ID["actor_rubric"], C_BLUE_L),
             "free_critic": (ARM_ID["free_critic"], C_BLUE_D),
             "thin_critic": (ARM_ID["thin_critic"], C_AMBER_D),
             "team_agg": (ARM_ID["team_agg"], C_AMBER)}
    _num = lambda v: None if v in ("", "-", None) else float(v)
    _dot = lambda n: max(15, min(220, 6 + n * 1.6))   # marker size ~ pooled n (tune on real n)
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ks = list(range(1, 9))
    if has_counts:
        agg = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # arm -> k -> [hits, n]
        for r in rows:
            h, nn = _num(r.get("hits")), _num(r.get("n"))
            if h is None or nn is None:
                continue
            cell = agg[r["arm"]][int(r["k"])]; cell[0] += h; cell[1] += nn
        for arm, (disp, col) in lines.items():
            xs, ys, ns = [], [], []
            for k in ks:
                h, nn = agg[arm].get(k, [0, 0])
                if nn > 0:
                    xs.append(k); ys.append(100 * h / nn); ns.append(nn)
            ax.plot(xs, ys, color=col, lw=2.0, zorder=3, label=disp)
            ax.scatter(xs, ys, s=[_dot(n) for n in ns], color=col,
                       edgecolor="white", linewidth=0.5, zorder=4)
        for nref in (5, 30, 100):                                # dot-size reference
            ax.scatter([], [], s=_dot(nref), color="#9AA6B2", edgecolor="white", label=f"n = {nref}")
    else:
        print("  [fig2] decay CSV lacks hits/n columns -> interim per-seed-mean render "
              "(jagged); regenerate once the neighbour adds count columns (single-source).")
        data = defaultdict(lambda: defaultdict(dict))
        for r in rows:
            if r.get("p") not in ("", "-", None):
                data[r["arm"]][int(r["k"])][int(r["seed"])] = float(r["p"])
        for arm, (disp, col) in lines.items():
            for s in SEEDS:
                pts = [(k, data[arm][k][s]) for k in ks if s in data[arm].get(k, {})]
                if pts:
                    ax.scatter([a for a, _ in pts], [b for _, b in pts], s=12, color=col,
                               alpha=0.35, edgecolor="none", zorder=2)
            mx, my = [], []
            for k in ks:
                vals = [data[arm][k][s] for s in SEEDS if s in data[arm].get(k, {})]
                if vals:
                    mx.append(k); my.append(sum(vals) / len(vals))
            ax.plot(mx, my, color=col, lw=2.4, zorder=4, label=disp)
    for k in (7, 8):
        ax.axvline(k, color="#999999", ls="--", lw=1.0, zorder=1)
        ax.text(k, 103, f"k={k}", ha="center", va="bottom", fontsize=8, color="#777777")
    ax.set_xlabel("k = step at which the batch first reaches tolerance")
    ax.set_ylabel("P(accept the batch | first in-tol at step k)   %")
    ax.set_xlim(0.7, 8.3); ax.set_ylim(-3, 108); ax.set_xticks(ks)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=9)
    save(fig, "fig2_decay_curve")


# ============================================================ FIG 3
def fig3_ablation(T1):
    abl = load_counts(RESULTS / "v3_ablation_weak_seed0.jsonl")
    S = lambda c: c.get("SUCCESS", 0); CF = lambda c: c.get("CRITICAL_FAIL", 0)
    t = T1["weak"][0]
    rows = [
        (ARM_ID["free_critic"], S(t["free_critic"]), CF(t["free_critic"]), C_BLUE),
        (ABL_ID["single_stoprule"], S(abl["single_stoprule"]), CF(abl["single_stoprule"]), C_BLUE),
        (ARM_ID["single"], S(t["single"]), CF(t["single"]), C_BLUE),
        ("", None, None, None),
        (ARM_ID["team_agg"], S(t["team_agg"]), CF(t["team_agg"]), C_BLUE),
        (ABL_ID["single_personaB"], S(abl["single_personaB"]), CF(abl["single_personaB"]), C_BLUE),
        (ARM_ID["single"] + " ", S(t["single"]), CF(t["single"]), C_BLUE),
        (" ", None, None, None),
        (ABL_ID["rubric_reassert"], S(abl["rubric_reassert"]), CF(abl["rubric_reassert"]), C_BLUE),
    ]
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ypos = list(range(len(rows)))[::-1]
    for y, (lab, s, cf, col) in zip(ypos, rows):
        if s is None:
            continue
        ax.barh(y, s, height=0.46, color=col, edgecolor="white", zorder=3)
        ax.text(s + 3, y, f"{s}", va="center", fontsize=8.5, color="#333333")
        ax.text(272, y, f"CF={cf}", va="center", ha="right", fontsize=8.5,
                color=C_CF, fontweight="bold")
        ax.text(-6, y, lab, va="center", ha="right", fontsize=8.8)
    ax.set_yticks([]); ax.set_xlim(0, 275); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel("SUCCESS  (/ 275, weak / Qwen2.5-32B, seed0)")
    save(fig, "fig3_ablation_channels")


# ============================================================ FIG 4
def fig4_safety(T1):
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.9))
    for ax, model in zip(axes, ("weak", "strong")):
        for a in ARMS:
            succ = [T1[model][s][a].get("SUCCESS", 0) for s in SEEDS]
            cf = [T1[model][s][a].get("CRITICAL_FAIL", 0) for s in SEEDS]
            ax.scatter(succ, cf, s=14, color=ARM_COLOR[a], alpha=0.30, zorder=3)
            ax.scatter([sum(succ) / 3], [sum(cf) / 3], s=72, color=ARM_COLOR[a],
                       edgecolor="white", linewidth=0.8, zorder=5)
        ax.set_xlabel("SUCCESS  (/ 275)")
        ax.text(0.0, 1.02, MODEL_ID[model], transform=ax.transAxes, fontsize=10,
                va="bottom", ha="left", color="#333333")
        ax.set_xlim(-8, 275)
    axes[0].set_ylabel("CRITICAL_FAIL  (/ 275)")
    arm_handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=ARM_COLOR[a],
                          markeredgecolor="white", markersize=8, label=ARM_ID[a]) for a in ARMS]
    style_handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor="#888",
                            markeredgecolor="white", markersize=9, label="arm mean (3 seeds)"),
                     Line2D([0], [0], marker="o", color="none", markerfacecolor="#888",
                            markersize=5, alpha=0.5, label="per-seed")]
    fig.legend(handles=arm_handles + style_handles, ncol=6, loc="lower center",
               frameon=False, bbox_to_anchor=(0.5, -0.08), fontsize=8.5)
    save(fig, "fig4_safety_success")


# ============================================================ FIG 5 -> table
def dump_three_layer_table():
    # Replaced the figure with a table (author's choice). Numbers from the three-seed
    # report section 6 (transcript-level), 3-seed s0/s1/s2.
    lines = ["# Three-layer diagnosis (weak vs strong) -- 3-seed s0/s1/s2\n",
             "| what is measured | weak | strong |",
             "|---|---|---|",
             "| corrective actions rejected by verifier (%) | 24/25/25 | 0/0/0 |",
             "| one corrective step reaches tolerance (%) | 28/31/29 | 97/97/96 |",
             "| batch accepted once in tolerance | 0/5518 terminal proposals | 0/90 last-step accepts |"]
    (OUT / "three_layer.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  wrote figures/three_layer.md (fig5 is now a table)")


# ============================================================ FIG 6 (optional)
def fig6_bury_rescue():
    # three-seed report section 4: team_vote selects 0/1/0 pool-accepts (buried 234/241/169),
    # team_agg selects 78/76/61 -> success 72/74/56.
    vote_sel, vote_succ = [0, 1, 0], [0, 1, 0]
    agg_sel, agg_succ = [78, 76, 61], [72, 74, 56]
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    x = [0, 1]
    ax.bar([i - 0.18 for i in x], [sum(vote_sel) / 3, sum(agg_sel) / 3], width=0.28,
           color=C_HANDOFF, edgecolor="white", label="accept proposals selected", zorder=3)
    ax.bar([i + 0.18 for i in x], [sum(vote_succ) / 3, sum(agg_succ) / 3], width=0.28,
           color=C_SUCCESS, edgecolor="white", label="resulting SUCCESS", zorder=3)
    for i, (sel, su) in enumerate([(vote_sel, vote_succ), (agg_sel, agg_succ)]):
        ax.scatter([i - 0.18] * 3, sel, s=14, color=C_SEED, zorder=5)
        ax.scatter([i + 0.18] * 3, su, s=14, color=C_SEED, zorder=5)
    ax.text(0, 14, "pool accepts:\n234 / 241 / 169", ha="center", fontsize=8, color="#666")
    ax.set_xticks(x); ax.set_xticklabels([ARM_ID["team_vote"], ARM_ID["team_agg"]])
    ax.set_ylabel("episodes  (/ 275)")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    save(fig, "fig6_bury_rescue")


def dump_maintable(T1):
    labmap = ", ".join(f"{ARM_ID[a]}={a}" for a in ARMS)
    lines = ["# Main table (exact numbers behind Fig 1) -- 3-seed, counts /275 as s0/s1/s2\n",
             f"Label map: {labmap}.\n",
             "| model | label | arm | SUCCESS | HANDOFF | UNMANAGED | CRITICAL_FAIL |",
             "|---|---|---|---|---|---|---|"]
    for model in ("weak", "strong"):
        for a in ARMS:
            cells = ["/".join(str(T1[model][s][a].get(t, 0)) for s in SEEDS)
                     for t in ("SUCCESS", "OVER_CONSERVATIVE", "UNMANAGED", "CRITICAL_FAIL")]
            lines.append(f"| {model} | {ARM_ID[a]} | {a} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    (OUT / "maintable.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  wrote figures/maintable.md")


def main():
    T1 = tier1()
    fig1_main(T1); fig2_decay(); fig3_ablation(T1); fig4_safety(T1)
    fig6_bury_rescue(); dump_three_layer_table(); dump_maintable(T1)
    print("done ->", OUT)


if __name__ == "__main__":
    main()
