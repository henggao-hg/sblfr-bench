"""bench_v3 master conformance gate (pure scripted, $0). Asserts the frozen contract:
params, 12-action set, 11 classes, Amendment G (observation no-leak / DROP), G3/G6/G7,
standards, recalibrate evidence-gate, scoring predicates, oracle paths, battery.
usage: python -m bench_v3.scripts.conformance_check
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench_v3.config import constants as C
from bench_v3.core.episode import run_episode
from bench_v3.core.verifier import verify
from bench_v3.core.observation import visible_observation, assert_no_leak, redact_action, INSTRUMENT_PUBLIC_FIELDS
from bench_v3.core.simulator import true_in_tol
from bench_v3.families.registry import sample_instance, certify_membership, all_class_specs
from bench_v3.families.base import build_scenario
from bench_v3.instances.oracle import cognitive_oracle
from bench_v3.instances.certify import certify_oracle
from bench_v3.prompts.base_actor import ALLOWED_ACTIONS_BLOCK

P = []
def chk(name, cond, detail=""):
    P.append(bool(cond)); print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))

rng = random.Random(99)
def get(fam, fc):
    for _ in range(4000):
        i = sample_instance(fam, fc, rng)
        if certify_membership(i) and certify_oracle(i)[0]:
            return i
    return None

print("=== parameters (spec section 10) ===")
chk("MAX_ACTIONS == 8", C.MAX_ACTIONS == 8)
chk("SIGMA == 0.01", C.SIGMA == 0.01)
chk("K_DETECT == 3", C.K_DETECT == 3)
chk("std ratios 0.25 / 2.0", C.STD_LOW_RATIO == 0.25 and C.STD_HIGH_RATIO == 2.0)

print("\n=== registries (N_FAMILIES=3, N_CLASSES=11, 12 actions) ===")
chk("3 families", C.N_FAMILIES == 3, str(C.N_FAMILIES))
chk("11 classes (sum over families, not len(CLASSES))", C.N_CLASSES == 11, str(C.N_CLASSES))
chk("12 actions", len(C.ACTIONS) == 12)
chk("wrong-species deleted", not any("species" in c for c in C.ALL_CLASSES))

print("\n=== Amendment G: observation no-leak / DROP calibration_status ===")
sim = build_scenario(get("f2", "instrument_recalibrate"), 0)
sim.state.instruments["assay_X"].calibration_status = "recalibrated"   # status set in STATE
obs = visible_observation(sim, [], 0)
iv = obs["instruments"]["assay_X"]
chk("instrument view == {measures, species}", iv == {"measures": "concentration", "species": "X"}, str(iv))
chk("no calibration_status / session_check in obs", set(iv) == set(INSTRUMENT_PUBLIC_FIELDS))
chk("assert_no_leak passes on clean obs", (assert_no_leak(obs) or True))
chk("redact_action strips extra key", redact_action({"type": "measure_volume", "vessel": "v", "calibration_status": "x"}) == {"type": "measure_volume", "vessel": "v"})
leaked = False
try:
    bad = visible_observation(sim, [], 0); bad["instruments"]["assay_X"]["calibration_status"] = "x"; assert_no_leak(bad)
except AssertionError:
    leaked = True
chk("assert_no_leak catches injected leak", leaked)

print("\n=== G3 termination / G6 reject-costs / G7 free-retry ===")
ep = run_episode(lambda o, retry=False: {"type": "measure_volume", "vessel": "vessel_1"}, build_scenario(get("f1", "no_fault"), 0))
chk("G3 measure-only exhausts budget (8), no early-exit", ep.actions_used == 8 and ep.terminal is None, f"steps={ep.actions_used}")
ep = run_episode(lambda o, retry=False: {"type": "discard_vessel", "vessel": "nope"}, build_scenario(get("f1", "no_fault"), 0))
chk("G6 illegal action costs budget (8)", ep.actions_used == 8)
def flaky(o, retry=False): return None if not retry else {"type": "accept_batch"}
ep = run_episode(flaky, build_scenario(get("f1", "no_fault"), 0))
chk("G7 first None -> free retry -> accept in 1 step", ep.terminal == "accept_batch" and ep.actions_used == 1)

print("\n=== recalibrate evidence-gate (Amendment D) ===")
sim = build_scenario(get("f2", "instrument_recalibrate"), 0)
ok, v = verify(sim, {"type": "recalibrate", "instrument": "assay_X"})
chk("bare recalibrate rejected (no standard)", (not ok) and v["resource_ok"] is False, v["reason"])

print("\n=== standards std_low=0.25x / std_high=2x ===")
i = get("f2", "instrument_recalibrate"); s = build_scenario(i, 0)
chk("std_low=0.25x", abs(s.state.standards["std_low"].certified_concentration_M - 0.25 * i.target_concentration_M) < 1e-6)
chk("std_high=2x", abs(s.state.standards["std_high"].certified_concentration_M - 2.0 * i.target_concentration_M) < 1e-6)

print("\n=== oracle reachability (every class SUCCESS in <=7) ===")
ok_all = True
for fam, fc in all_class_specs():
    i = get(fam, fc)
    if i is None:
        ok_all = False; continue
    passed, steps = certify_oracle(i)
    ok_all = ok_all and passed and steps <= 7
chk("all 11 classes certify (SUCCESS+fault_cleared, <=7 steps)", ok_all)

print("\n=== prompt action block lists all 12 ===")
chk("prompt has all 12 action types", all(a in ALLOWED_ACTIONS_BLOCK for a in C.ACTIONS))
chk("prompt recalibrate line has no fault-family word", "gain" not in ALLOWED_ACTIONS_BLOCK and "bias" not in ALLOWED_ACTIONS_BLOCK)

print(f"\n===== TOTAL: {sum(P)}/{len(P)} PASS =====")
sys.exit(0 if all(P) else 1)
