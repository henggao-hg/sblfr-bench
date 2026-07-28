"""SBLFR-Chem v1 simulator core — shared by F1 (Transfer/Dilution) and F3
(Reagent Quality / Identity) scenarios.

Design choices
--------------
* `Stock` carries both visible (ledger / label) and hidden (true) fields. F1
  uses the volume divergence; F3 will use the species / concentration
  divergence. F1 scenarios leave the F3 extension fields at their default
  ("no divergence") values.
* `HiddenTruth` is intentionally NOT defined here — each scenario module
  defines its own dataclass (different fault families have different hidden
  state). `Simulator` only requires `hidden` to be opaque to it.
* `Simulator` is a **nominal** simulator (no fault injection). Scenarios
  subclass it and override hook methods like `_effective_transfer_volume`
  to inject faults. This keeps fault models local to the scenario.
"""
from __future__ import annotations
import copy
import os
import random
from dataclasses import dataclass, field


# ============================================================================
# State
# ============================================================================

@dataclass
class Vessel:
    name: str
    volume_ml: float          # visible: liquid level is observable in a real lab
    capacity_ml: float
    species_mmol: dict[str, float] = field(default_factory=dict)  # HIDDEN

    def concentration_M(self, species: str) -> float:
        if self.volume_ml <= 0:
            return 0.0
        return self.species_mmol.get(species, 0.0) / self.volume_ml


@dataclass
class Stock:
    name: str
    species: str                          # label species (visible)
    label_concentration_M: float          # visible
    ledger_volume_remaining_ml: float     # visible (bookkeeping)
    true_volume_remaining_ml: float       # HIDDEN: F1 fault signature
    # F3 extension slots (default = no divergence between label and true).
    true_species: str | None = None
    true_concentration_M: float | None = None
    # Quarantine flag. Set via the `quarantine_stock` action; once True the
    # verifier rejects any further `transfer` from this stock. Visible to
    # the agent through the observation dict.
    quarantined: bool = False

    def get_true_species(self) -> str:
        return self.true_species if self.true_species is not None else self.species

    def get_true_concentration_M(self) -> float:
        return (self.true_concentration_M
                if self.true_concentration_M is not None
                else self.label_concentration_M)


@dataclass
class Standard:
    """A certified reference standard of known true concentration. Used by F2
    (instrument/calibration faults) so an agent can measure a known-truth
    sample to disambiguate an instrument fault from a real process deviation.
    The certified concentration is VISIBLE to the agent; the instrument fault
    (if any) is applied to the reading of this standard just like any vessel,
    so a biased instrument reads the standard off by the same transform."""
    name: str
    species: str
    certified_concentration_M: float       # visible: known true value
    available_volume_ml: float = 10.0


@dataclass
class Instrument:
    """A measuring instrument with a calibration status. Used by F2. The
    actual fault (bias/gain parameters) lives in the scenario's hidden truth,
    not here; this is only the agent-visible record (label + status)."""
    name: str
    measures: str                          # e.g. "concentration"
    species: str | None = None
    calibration_status: str = "unknown"     # "unknown" | "recalibrated"
    read_count: int = 0                     # F2 drift: # of committed reads on
                                            # this instrument (drives time-varying
                                            # drift = B * read_count). In state so
                                            # the dry-run snapshot protects it.


@dataclass
class State:
    vessels: dict[str, Vessel] = field(default_factory=dict)
    stocks: dict[str, Stock] = field(default_factory=dict)
    measurement_budget: int = 5
    step_count: int = 0
    log: list = field(default_factory=list)
    # F2 extension slots. Default empty so F1/F3 State (and their observation)
    # are byte-for-byte unchanged.
    standards: dict[str, "Standard"] = field(default_factory=dict)
    instruments: dict[str, "Instrument"] = field(default_factory=dict)

    def snapshot(self) -> "State":
        return copy.deepcopy(self)


# ============================================================================
# Schema validation (stage 1)
# ============================================================================

ACTION_SCHEMA: dict[str, dict] = {
    "transfer":             {"required": ["src", "dst", "volume_ml"],
                             "numeric": ["volume_ml"]},
    "dilute_to":            {"required": ["vessel", "target_volume_ml"],
                             "numeric": ["target_volume_ml"]},
    "measure_concentration":{"required": ["vessel", "species"], "numeric": []},
    "measure_volume":       {"required": ["vessel"], "numeric": []},
    "measure_stock_volume": {"required": ["stock"], "numeric": []},
    "discard_vessel":       {"required": ["vessel"], "numeric": []},
    "quarantine_stock":     {"required": ["stock"], "numeric": []},
    "accept_low_yield":     {"required": [], "numeric": []},
    "abort_and_handoff":    {"required": ["reason"], "numeric": []},
}


ResourceValidator = "callable: (state, action) -> tuple[bool, str]"
_EXTENSION_RESOURCE_VALIDATORS: dict = {}


def register_action(name: str, *, required: list[str],
                    numeric: list[str] | None = None,
                    resource_validator=None) -> None:
    """Scenarios call this at import time to add scenario-specific actions
    (e.g. F3's `quarantine_stock`).

    `resource_validator(state, action) -> (ok, reason)` is optional but
    strongly recommended: without it `validate_resources` will accept any
    well-formed action regardless of state, which means a missing stock /
    unknown vessel only surfaces as a runtime error inside `_apply_extension`.
    Pass `resource_validator=None` only for actions with no resource
    preconditions (analogous to built-in `accept_low_yield`).
    """
    ACTION_SCHEMA[name] = {"required": required, "numeric": numeric or []}
    if resource_validator is not None:
        _EXTENSION_RESOURCE_VALIDATORS[name] = resource_validator
    elif name in _EXTENSION_RESOURCE_VALIDATORS:
        # re-registering without a validator: clear stale entry
        del _EXTENSION_RESOURCE_VALIDATORS[name]


def validate_action_schema(action: dict) -> tuple[bool, str]:
    if not isinstance(action, dict):
        return False, "action must be a JSON object"
    atype = action.get("type")
    if atype not in ACTION_SCHEMA:
        return False, f"unknown action type '{atype}'; allowed: {list(ACTION_SCHEMA)}"
    spec = ACTION_SCHEMA[atype]
    missing = [k for k in spec["required"] if k not in action]
    if missing:
        return False, f"missing required field(s): {missing}"
    for k in spec["numeric"]:
        try:
            float(action[k])
        except (TypeError, ValueError):
            return False, (f"field '{k}' must be a number (got {action[k]!r})")
    return True, "ok"


# ============================================================================
# Resource validation (stage 2)
# ============================================================================

def validate_resources(state: State, action: dict) -> tuple[bool, str]:
    atype = action["type"]
    if atype in _EXTENSION_RESOURCE_VALIDATORS:
        return _EXTENSION_RESOURCE_VALIDATORS[atype](state, action)
    if atype == "transfer":
        src = state.stocks.get(action["src"])
        dst = state.vessels.get(action["dst"])
        if src is None:
            return False, f"unknown stock '{action['src']}'"
        if dst is None:
            return False, f"unknown vessel '{action['dst']}'"
        if src.quarantined:
            return False, (f"stock '{src.name}' is quarantined and cannot be "
                           f"used for further transfers")
        vol = float(action["volume_ml"])
        if vol <= 0:
            return False, f"transfer volume must be positive (got {vol})"
        if vol > src.ledger_volume_remaining_ml + 1e-9:
            return False, (f"insufficient stock '{src.name}' per ledger: "
                           f"requested {vol} mL, ledger has "
                           f"{src.ledger_volume_remaining_ml} mL")
        if dst.volume_ml + vol > dst.capacity_ml + 1e-9:
            headroom = dst.capacity_ml - dst.volume_ml
            return False, (f"vessel '{dst.name}' capacity exceeded: "
                           f"requested +{vol} mL, headroom {headroom:.2f} mL")
    elif atype == "dilute_to":
        v = state.vessels.get(action["vessel"])
        if v is None:
            return False, f"unknown vessel '{action['vessel']}'"
        target = float(action["target_volume_ml"])
        if target > v.capacity_ml + 1e-9:
            return False, (f"vessel '{v.name}' capacity exceeded: target "
                           f"{target} mL > capacity {v.capacity_ml} mL")
        if target < v.volume_ml - 1e-9:
            return False, (f"cannot dilute below current volume ({v.volume_ml} mL)")
    elif atype in ("measure_concentration", "measure_volume", "measure_stock_volume"):
        if state.measurement_budget <= 0:
            return False, "measurement budget exhausted"
        if atype == "measure_concentration":
            if action["vessel"] not in state.vessels:
                return False, f"unknown vessel '{action['vessel']}'"
        elif atype == "measure_volume":
            if action["vessel"] not in state.vessels:
                return False, f"unknown vessel '{action['vessel']}'"
        else:
            if action["stock"] not in state.stocks:
                return False, f"unknown stock '{action['stock']}'"
    elif atype == "discard_vessel":
        if action["vessel"] not in state.vessels:
            return False, f"unknown vessel '{action['vessel']}'"
    elif atype == "quarantine_stock":
        if action["stock"] not in state.stocks:
            return False, f"unknown stock '{action['stock']}'"
    # accept_low_yield and abort_and_handoff have no resource preconditions
    return True, "ok"


# ============================================================================
# Invariants (stage 4)
# ============================================================================

def check_invariants(state: State) -> tuple[bool, list[str]]:
    violations: list[str] = []
    for v in state.vessels.values():
        if v.volume_ml < -1e-9:
            violations.append(f"negative volume in vessel '{v.name}'")
        if v.volume_ml > v.capacity_ml + 1e-9:
            violations.append(f"capacity exceeded in vessel '{v.name}'")
        for sp, n in v.species_mmol.items():
            if n < -1e-9:
                violations.append(f"negative moles of {sp} in vessel '{v.name}'")
    for s in state.stocks.values():
        if s.true_volume_remaining_ml < -1e-9:
            violations.append(f"negative true stock volume in '{s.name}'")
        if s.ledger_volume_remaining_ml < -1e-9:
            violations.append(f"negative ledger stock volume in '{s.name}'")
    return (not violations), violations


# ============================================================================
# Goal residual (stage 5)
# ============================================================================

def goal_residual(state: State, goal: dict) -> float:
    v = state.vessels[goal["vessel"]]
    return v.concentration_M(goal["species"]) - goal["target_concentration_M"]


def goal_met(state: State, goal: dict, tol_M: float | None = None) -> bool:
    """Tolerance precedence: explicit arg > goal['tolerance_M'] > 0.005 default."""
    tol = tol_M if tol_M is not None else goal.get("tolerance_M", 0.005)
    return abs(goal_residual(state, goal)) <= tol


# ============================================================================
# Simulator (nominal; subclasses inject scenario faults)
# ============================================================================

class Simulator:
    """Nominal env.step pipeline.

    Pipeline: schema -> resources -> transition -> invariants -> goal.
    Supports `dry_run` (no RNG side effects, no state mutation).

    Fault injection is **not** in this base class — scenarios subclass and
    override hooks like `_effective_transfer_volume` to apply faults.
    """

    def __init__(self, state: State, hidden, rng: random.Random):
        self.state = state
        self.hidden = hidden
        self.rng = rng
        self._goal = None

    def set_goal(self, goal: dict) -> None:
        self._goal = goal

    # ---- public ----

    def step(self, action: dict, *, inject_fault: bool, dry_run: bool = False) -> dict:
        try:
            return self._step_inner(action, inject_fault=inject_fault, dry_run=dry_run)
        except Exception as exc:
            return {
                "schema_ok": None, "resource_ok": None,
                "invariants_ok": None, "goal_residual_before": None,
                "goal_residual_after": None, "improvement": None,
                "reason": f"runtime: {type(exc).__name__}: {exc}",
                "observation": None, "dry_run": dry_run,
            }

    def _step_inner(self, action: dict, *, inject_fault: bool, dry_run: bool) -> dict:
        # Default check fields to None ("not reached"). Each validation
        # gate explicitly sets True/False as it runs. This way a resource
        # rejection no longer claims invariants_ok=False (the invariants
        # check did not run for that attempt).
        feedback = {
            "schema_ok": None, "resource_ok": None,
            "invariants_ok": None, "goal_residual_before": None,
            "goal_residual_after": None, "improvement": None,
            "reason": None, "observation": None, "dry_run": dry_run,
        }
        ok, reason = validate_action_schema(action)
        feedback["schema_ok"] = ok
        if not ok:
            feedback["reason"] = f"schema: {reason}"
            return feedback

        ok, reason = validate_resources(self.state, action)
        feedback["resource_ok"] = ok
        if not ok:
            feedback["reason"] = f"resource: {reason}"
            return feedback

        residual_before = (goal_residual(self.state, self._goal)
                           if self._goal else None)
        feedback["goal_residual_before"] = (round(residual_before, 5)
                                            if residual_before is not None else None)

        if dry_run:
            saved_state = self.state
            self.state = saved_state.snapshot()
            try:
                obs = self._apply(action, inject_fault=False, draw_noise=False)
            finally:
                snap_state = self.state
                self.state = saved_state
            inv_ok, inv_vio = check_invariants(snap_state)
            feedback["invariants_ok"] = inv_ok
            if not inv_ok:
                feedback["reason"] = "invariants: " + "; ".join(inv_vio)
                return feedback
            residual_after = (goal_residual(snap_state, self._goal)
                              if self._goal else None)
            feedback["goal_residual_after"] = (round(residual_after, 5)
                                               if residual_after is not None else None)
            if residual_before is not None and residual_after is not None:
                feedback["improvement"] = round(
                    abs(residual_before) - abs(residual_after), 5)
            feedback["observation"] = obs
            feedback["reason"] = "ok"
            return feedback

        obs = self._apply(action, inject_fault=inject_fault, draw_noise=True)
        self.state.step_count += 1
        inv_ok, inv_vio = check_invariants(self.state)
        feedback["invariants_ok"] = inv_ok
        if not inv_ok:
            feedback["reason"] = "invariants: " + "; ".join(inv_vio)
            return feedback
        residual_after = (goal_residual(self.state, self._goal)
                          if self._goal else None)
        feedback["goal_residual_after"] = (round(residual_after, 5)
                                           if residual_after is not None else None)
        if residual_before is not None and residual_after is not None:
            feedback["improvement"] = round(
                abs(residual_before) - abs(residual_after), 5)
        feedback["observation"] = obs
        # Enrich the per-action log entry with verifier outputs so the
        # blackboard action_log carries residual/reason for every step
        # without needing a separate verifier-feedback channel.
        if self.state.log:
            self.state.log[-1]["goal_residual_before"] = feedback["goal_residual_before"]
            self.state.log[-1]["goal_residual_after"] = feedback["goal_residual_after"]
            self.state.log[-1]["improvement"] = feedback.get("improvement")
            self.state.log[-1]["reason"] = "ok"
        feedback["reason"] = "ok"
        return feedback

    # ---- dispatch ----

    def _apply(self, action: dict, *, inject_fault: bool, draw_noise: bool) -> dict:
        atype = action["type"]
        if atype == "transfer":
            return self._transfer(action, inject_fault=inject_fault)
        if atype == "dilute_to":
            return self._dilute_to(action)
        if atype == "measure_concentration":
            return self._measure_concentration(action, draw_noise=draw_noise)
        if atype == "measure_volume":
            return self._measure_volume(action, draw_noise=draw_noise)
        if atype == "measure_stock_volume":
            return self._measure_stock_volume(action, draw_noise=draw_noise)
        if atype == "discard_vessel":
            return self._discard_vessel(action)
        if atype == "quarantine_stock":
            return self._quarantine_stock(action)
        if atype == "accept_low_yield":
            return {"acknowledged": "accept_low_yield"}
        if atype == "abort_and_handoff":
            return {"acknowledged": "abort_and_handoff",
                    "reason": action.get("reason", "")}
        return self._apply_extension(action, inject_fault=inject_fault,
                                     draw_noise=draw_noise)

    def _apply_extension(self, action: dict, *,
                         inject_fault: bool, draw_noise: bool) -> dict:
        """Hook for scenarios that registered extra action types."""
        raise ValueError(f"unhandled action {action.get('type')!r}")

    # ---- scenario hooks ----

    def _effective_transfer_volume(self, action: dict, *,
                                   inject_fault: bool) -> float:
        """Nominal: actual volume = requested. F1 overrides this to inject
        under-delivery faults."""
        return float(action["volume_ml"])

    def _effective_transfer_concentration_M(self, src: Stock) -> float:
        """Nominal: label concentration. F3 will override to return the true
        (mis-labelled) concentration during fault injection."""
        return src.label_concentration_M

    def _effective_transfer_species(self, src: Stock) -> str:
        """Nominal: label species. F3 will override for identity faults."""
        return src.species

    def _instrument_reading(self, true_value: float, species: str) -> float:
        """Nominal: the instrument reads the true value faithfully. F2
        overrides this to inject a persistent calibration fault, e.g.
        additive bias (return true + A) or multiplicative gain (return
        G * true). The same transform is applied to vessel measurements and
        to reference-standard measurements, which is what makes a
        single reading ambiguous between an instrument fault and a real
        process deviation."""
        return true_value

    # ---- nominal action handlers ----

    def _transfer(self, action: dict, *, inject_fault: bool) -> dict:
        src = self.state.stocks[action["src"]]
        dst = self.state.vessels[action["dst"]]
        requested_ml = float(action["volume_ml"])
        actual_ml = self._effective_transfer_volume(
            action, inject_fault=inject_fault)
        conc = self._effective_transfer_concentration_M(src)
        species = self._effective_transfer_species(src)

        src.ledger_volume_remaining_ml -= requested_ml
        src.true_volume_remaining_ml -= actual_ml
        delivered_mmol = actual_ml * conc
        dst.volume_ml += actual_ml
        dst.species_mmol[species] = dst.species_mmol.get(species, 0.0) + delivered_mmol

        self.state.log.append({
            "step": self.state.step_count, "action": "transfer",
            "src": src.name, "dst": dst.name,
            "requested_ml": requested_ml,
        })
        return {"action": "transfer", "requested_ml": requested_ml,
                "completed": True}

    def _dilute_to(self, action: dict) -> dict:
        v = self.state.vessels[action["vessel"]]
        target = float(action["target_volume_ml"])
        v.volume_ml = target
        self.state.log.append({
            "step": self.state.step_count, "action": "dilute_to",
            "vessel": v.name, "target_volume_ml": target,
        })
        return {"action": "dilute_to", "final_volume_ml": target}

    def _measure_concentration(self, action: dict, *, draw_noise: bool) -> dict:
        v = self.state.vessels[action["vessel"]]
        sp = action["species"]
        true_C = v.concentration_M(sp)
        if not draw_noise:
            return {"action": "measure_concentration", "dry_run": True,
                    "would_consume_budget": 1}
        # Relative noise so high-concentration and low-concentration instances
        # share comparable difficulty. v1 used a fixed absolute σ = 0.003 M,
        # which made low-concentration / tight-tolerance instances essentially
        # unmeasurable (σ > tol on ~40% of the corpus). Relative noise tied to
        # the goal target ties σ to the same scale as tolerance.
        goal_target_C = self._goal.get("target_concentration_M") if self._goal else None
        base_C = goal_target_C if goal_target_C is not None else max(true_C, 1e-3)
        sigma = 0.01 * max(base_C, 1e-3)
        # Instrument transform (F2): the displayed value is what the instrument
        # reports for the true concentration. Nominal = identity, so F1/F3 are
        # unaffected. Measurement noise is added AFTER the instrument transform
        # (the instrument first reads true*G+A, then read noise is added).
        displayed_C = self._instrument_reading(true_C, sp)
        noisy = max(0.0, displayed_C + self.rng.gauss(0, sigma))
        self.state.measurement_budget -= 1
        entry = {"step": self.state.step_count, "action": "measure_concentration",
                 "vessel": v.name, "species": sp, "observed_M": round(noisy, 4)}
        self.state.log.append(entry)
        return {**entry, "measurement_budget_remaining": self.state.measurement_budget}

    def _measure_volume(self, action: dict, *, draw_noise: bool) -> dict:
        v = self.state.vessels[action["vessel"]]
        if not draw_noise:
            return {"action": "measure_volume", "dry_run": True,
                    "would_consume_budget": 1}
        noisy = v.volume_ml + self.rng.gauss(0, 0.3)
        self.state.measurement_budget -= 1
        entry = {"step": self.state.step_count, "action": "measure_volume",
                 "vessel": v.name, "observed_ml": round(noisy, 2)}
        self.state.log.append(entry)
        return {**entry, "measurement_budget_remaining": self.state.measurement_budget}

    def _measure_stock_volume(self, action: dict, *, draw_noise: bool) -> dict:
        s = self.state.stocks[action["stock"]]
        if not draw_noise:
            return {"action": "measure_stock_volume", "dry_run": True,
                    "would_consume_budget": 1}
        noisy = s.true_volume_remaining_ml + self.rng.gauss(0, 0.3)
        self.state.measurement_budget -= 1
        entry = {"step": self.state.step_count, "action": "measure_stock_volume",
                 "stock": s.name, "observed_ml": round(noisy, 2)}
        self.state.log.append(entry)
        return {**entry, "measurement_budget_remaining": self.state.measurement_budget}

    def _discard_vessel(self, action: dict) -> dict:
        v = self.state.vessels[action["vessel"]]
        v.volume_ml = 0.0
        v.species_mmol = {}
        self.state.log.append({"step": self.state.step_count,
                               "action": "discard_vessel", "vessel": v.name})
        return {"action": "discard_vessel", "vessel": v.name}

    def _quarantine_stock(self, action: dict) -> dict:
        s = self.state.stocks[action["stock"]]
        s.quarantined = True
        self.state.log.append({"step": self.state.step_count,
                               "action": "quarantine_stock", "stock": s.name})
        return {"action": "quarantine_stock", "stock": s.name,
                "quarantined": True}


# ============================================================================
# Operator (thin executor)
# ============================================================================

class Operator:
    """Thin execution wrapper around the simulator. NOT the LLM Operator
    Agent — that lives in ``multi_agent/operator_agent.py`` (v1.5).

    This class is effectively an Executor: given a typed action, it hands
    it to the simulator with ``dry_run=False`` and returns the verifier's
    committed feedback. The name "Operator" predates the multi-agent split
    (in the lab_repair_framwork architecture figure, the Operator is one
    of three LLM agents); the v1 single-agent loop never used an LLM for
    the operator role and kept this thin wrapper instead. v1.5
    (``multi_agent/operator_agent.py``) is the actual LLM Operator Agent
    with its own tool-use loop and protocol planning. Both still depend
    on this Executor class to commit actions, so renaming it cascades —
    we keep the class name and rely on this docstring to disambiguate.

    Dry-run gating belongs to the Verifier (i.e. ``sim.step(..., dry_run=True)``
    called directly by the recovery loop) and is intentionally NOT exposed
    here — calling ``Operator.execute`` always commits.
    """

    def __init__(self, sim: Simulator):
        self.sim = sim

    def execute(self, action: dict, *, inject_fault: bool) -> dict:
        return self.sim.step(action, inject_fault=inject_fault, dry_run=False)


# ============================================================================
# Agent-facing observation (hides ground truth)
# ============================================================================

def state_observation_for_agent(state: State, goal: dict,
                                last_feedback: dict | None,
                                *,
                                attempts_used: int | None = None,
                                max_attempts: int | None = None,
                                nominal_steps: int = 2,
                                attempts_log: list | None = None,
                                initial_protocol_record: list | None = None
                                ) -> dict:
    """Build the agent-visible observation.

    v1 (default, SBLFR_BLACKBOARD unset): exposes vessel/stock state, the
    last 5 measurements, the most recent verifier feedback, and a
    measurement budget. Earlier transfer/dilute/discard actions are not
    surfaced directly — agents must reconstruct intermediate state from
    current vessel volume and stock ledger.

    v2 (SBLFR_BLACKBOARD=1): replaces the partial-history fields with a
    shared blackboard: a full `action_log` (every recovery attempt,
    committed or rejected, with the verifier outcome embedded) and an
    `action_budget` block (actions_used / actions_remaining /
    max_actions). The measurement budget remains a verifier-side
    constraint but is not surfaced as a separate counter to the agent;
    the action budget is the single externally visible resource. When
    `initial_protocol_record` is supplied (the nominal protocol that
    Operator submitted before the recovery loop began), it is included
    as a lab-notebook history field so the agent can recover the
    original plan after destructive actions like discard_vessel.

    Args:
        attempts_used: number of recovery attempts already committed (the
            caller's loop knows this; the simulator's step_count includes
            nominal protocol steps, so we cannot infer it here without
            knowing how many nominal steps there were).
        max_attempts: total recovery attempt budget for the episode.
        nominal_steps: how many initial steps of state.log are the nominal
            protocol (which should be excluded from the recovery action
            log). Default 2 for F1/F3 (transfer + dilute_to).
        attempts_log: caller-maintained list of every proposed action
            (committed or rejected). Becomes `action_log` in v2.
        initial_protocol_record: the nominal protocol that was executed
            before recovery (list of action dicts). Added to v2 as
            `initial_protocol_record` to surface the original plan to
            the recovery agent. Single-agent passes the scripted
            protocol; multi-agent passes the Operator's submitted
            protocol.
    """
    use_blackboard = os.environ.get("SBLFR_BLACKBOARD", "0") == "1"
    obs: dict = {
        "goal": goal,
        "vessels": {
            name: {
                "volume_ml": round(v.volume_ml, 3),
                "capacity_ml": v.capacity_ml,
            }
            for name, v in state.vessels.items()
        },
        "stocks": {
            name: {
                "species": s.species,
                "label_concentration_M": s.label_concentration_M,
                "ledger_volume_remaining_ml": round(s.ledger_volume_remaining_ml, 3),
                "quarantined": s.quarantined,
            }
            for name, s in state.stocks.items()
        },
    }
    # F2 fields: only added when present, so F1/F3 observations are unchanged.
    if state.standards:
        obs["standards"] = {
            name: {
                "species": st.species,
                "certified_concentration_M": st.certified_concentration_M,
                "available_volume_ml": round(st.available_volume_ml, 3),
            }
            for name, st in state.standards.items()
        }
    if state.instruments:
        obs["instruments"] = {
            name: {
                "measures": ins.measures,
                "species": ins.species,
                "calibration_status": ins.calibration_status,
            }
            for name, ins in state.instruments.items()
        }
    if use_blackboard:
        # v2 blackboard: every attempt (committed or rejected) lives in
        # action_log with its verifier outcome. Rejections include parse
        # failures, schema/resource/invariant violations, and runtime
        # exceptions. Because action_log carries every attempt, we drop
        # the separate last_verifier_feedback channel — it was only
        # needed in v1 to expose rejection reasons that did not enter
        # state.log.
        if initial_protocol_record is not None:
            obs["initial_protocol_record"] = list(initial_protocol_record)
        obs["action_log"] = list(attempts_log) if attempts_log else []
        # "action_budget" (not "budget") to distinguish from any LLM-side
        # retry budget and to align with the agent-facing "actions" framing.
        action_budget: dict = {}
        if max_attempts is not None and attempts_used is not None:
            action_budget["actions_used"] = attempts_used
            action_budget["actions_remaining"] = max_attempts - attempts_used
            action_budget["max_actions"] = max_attempts
        obs["action_budget"] = action_budget
    else:
        # v1 partial-history observation (unchanged from earlier releases).
        obs["measurement_budget"] = state.measurement_budget
        obs["recent_measurements"] = [
            e for e in state.log
            if e.get("action", "").startswith("measure_")
        ][-5:]
        obs["last_verifier_feedback"] = last_feedback
    return obs
