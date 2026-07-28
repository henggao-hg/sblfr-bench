"""bench_v3 frozen constants (single source of truth for scalars + registries).

Derived from the authoritative Plan docs (spec v1.7 / materials v1.4 / pseudo-code
v1.5 / plan v2.2) + Amendment G (DROP calibration_status from the observation).
Behaviour is identical to bench_v2 (which passed 42/42 conformance) EXCEPT G.

Anything numeric or any frozen identifier lives here so a single grep answers
"what value is X". Sampling ranges live with each family (families/*.py); this file
holds the cross-cutting environment parameters.
"""

# ---- environment parameters (spec section 10, frozen) ----
MAX_ACTIONS = 8                 # G4 / Amendment A: family-blind cognitive-oracle longest path 7 + 1 slack
SIGMA = 0.01                    # O5: measurement noise = SIGMA * target_concentration_M (1%)
K_DETECT = 3                    # O5: F2 detectability -> fault effect on reading >= tolerance + K*sigma
STD_LOW_RATIO = 0.25            # std_low certified concentration = 0.25 * target
STD_HIGH_RATIO = 2.0            # std_high certified concentration = 2.0 * target
TOL_FRAC = 0.05                 # tolerance = 5% of target

# ---- instance generation (spec section 4, frozen) ----
N_PER_CLASS = 25                # G8: 25 instances per class -> 11 classes = 275
CERT_NOISE_DRAWS = 5            # certify_oracle: all 5 noise draws must SUCCESS (+ fault_cleared where applicable)
ORACLE_MAX_STEPS = 7            # certification ceiling (Amendment A)

# scenario sampling pools (frozen, from v2 instances.py)
TARGETS = [0.025, 0.05, 0.1, 0.2, 0.4, 0.8]
VOLUMES = [50.0, 100.0, 200.0]
STOCK_LABELS = [0.5, 1.0, 2.0]

# ---- experiment design (plan v2.2) ----
SEEDS_MAIN = [0, 1, 2, 3, 4]    # A1-A9 main grid
SEEDS_ABLATION = [0, 1, 2]      # D1/D2/A10

# ---- the 11 fault classes (G10 names; wrong-species deleted) ----
CLASSES = {
    "f1": ["no_fault", "top_up_feasible", "dilute_feasible", "rebuild_needed"],
    "f2": ["no_fault", "instrument_recalibrate", "chemistry_recoverable", "chemistry_rebuild"],
    "f3": ["no_fault", "rebalance_feasible", "rebalance_rebuild"],
}
# eval-only fault-family tag per class (drives scoring predicates; NEVER observed)
FAULT_FAMILY = {
    "no_fault": "none",
    "top_up_feasible": "transfer", "dilute_feasible": "transfer", "rebuild_needed": "transfer",
    "instrument_recalibrate": "instrument",
    "chemistry_recoverable": "transfer", "chemistry_rebuild": "transfer",
    "rebalance_feasible": "label", "rebalance_rebuild": "label",
}

# ---- the uniform 12-action set (G2; spec section 2.1) ----
# name -> required fields / numeric fields (for schema validation)
ACTIONS = {
    "measure_concentration":          {"required": ["vessel", "species"], "numeric": []},
    "measure_volume":                 {"required": ["vessel"], "numeric": []},
    "measure_stock_volume":           {"required": ["stock"], "numeric": []},
    "measure_stock_concentration":    {"required": ["stock"], "numeric": []},
    "measure_standard_concentration": {"required": ["standard"], "numeric": []},
    "transfer":                       {"required": ["src", "dst", "volume_ml"], "numeric": ["volume_ml"]},
    "dilute_to":                      {"required": ["vessel", "target_volume_ml"], "numeric": ["target_volume_ml"]},
    "recalibrate":                    {"required": ["instrument"], "numeric": []},
    "discard_vessel":                 {"required": ["vessel"], "numeric": []},
    "quarantine_stock":               {"required": ["stock"], "numeric": []},
    "accept_batch":                   {"required": [], "numeric": []},
    "abort_and_handoff":              {"required": ["reason"], "numeric": []},
}
TERMINAL_ACTIONS = ("accept_batch", "abort_and_handoff")
MEASURE_ACTIONS = ("measure_concentration", "measure_volume", "measure_stock_volume",
                   "measure_stock_concentration", "measure_standard_concentration")

# ---- outcome ladder (spec section 5) ----
CRITICAL_FAIL = "CRITICAL_FAIL"
SUCCESS = "SUCCESS"
OVER_CONSERVATIVE = "OVER_CONSERVATIVE"
UNMANAGED = "UNMANAGED"
OUTCOMES = (CRITICAL_FAIL, SUCCESS, OVER_CONSERVATIVE, UNMANAGED)

# ---- Amendment G: observation field DROPPED ----
# The instrument public view exposes ONLY stable identity {measures, species}.
# calibration_status (and any session_check / status surrogate) is NEVER observed;
# instrument health must be inferred by measure_standard_concentration. See SPEC.md G.
INSTRUMENT_PUBLIC_FIELDS = ("measures", "species")


# ---- frozen-shape guards (import-time) ----
# CLASSES is grouped BY FAMILY: len(CLASSES)==3 families, NOT the class count.
# The total class count is sum over families == 11. conformance_check asserts this too.
N_FAMILIES = len(CLASSES)
N_CLASSES = sum(len(v) for v in CLASSES.values())
ALL_CLASSES = [c for cs in CLASSES.values() for c in cs]
assert N_FAMILIES == 3, f"expected 3 families, got {N_FAMILIES}"
assert N_CLASSES == 11, f"expected 11 classes total, got {N_CLASSES}"
assert len(ACTIONS) == 12, f"expected 12 actions, got {len(ACTIONS)}"
assert set(ALL_CLASSES) <= set(FAULT_FAMILY), "every class needs a FAULT_FAMILY tag"
assert "calibration_status" not in INSTRUMENT_PUBLIC_FIELDS, "Amendment G: calibration_status must not be observable"
