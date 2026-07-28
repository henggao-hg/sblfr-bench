"""Oracle reachability certification. Runs the cognitive oracle as a scripted policy
under CERT_NOISE_DRAWS noise seeds; keep an instance only if EVERY draw reaches SUCCESS
in <= ORACLE_MAX_STEPS AND fault_cleared (where the class has an actionable fault,
Amendment E2 -- so the cert pipeline exercises the calibration mechanism). Ported from
bench_v2 oracle.certify_oracle. (Membership cert lives in families/registry.certify_membership.)
"""
from __future__ import annotations

from bench_v3.config.constants import CERT_NOISE_DRAWS, ORACLE_MAX_STEPS, SUCCESS
from bench_v3.families.base import build_scenario
from bench_v3.core.episode import run_episode
from bench_v3.scoring.outcomes import score
from bench_v3.scoring.secondary import fault_cleared
from bench_v3.instances.oracle import cognitive_oracle


def certify_oracle(inst) -> tuple[bool, int]:
    max_steps = 0
    for draw in range(CERT_NOISE_DRAWS):
        sim = build_scenario(inst, noise_seed=1000 + draw)
        ep = run_episode(cognitive_oracle, sim)
        if score(ep, inst) != SUCCESS or ep.actions_used > ORACLE_MAX_STEPS:
            return False, ep.actions_used
        if fault_cleared(ep, inst) is False:        # Amendment E2 (instrument class)
            return False, ep.actions_used
        max_steps = max(max_steps, ep.actions_used)
    return True, max_steps
