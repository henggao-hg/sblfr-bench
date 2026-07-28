"""The episode loop. G3 (terminal-only end), G6 (rejected costs budget), G7 (one free
parse retry). Builds the agent-visible action_log (redacted) AND the eval-only steps
transcript (full action incl rationale, verifier, result, per-step truth, per-step
tokens, critic/proposal audit). Ported from bench_v2 env.run_episode.

policy(obs, retry=False) -> action dict or None. A policy may attach eval-only
'_critic' / '_proposals' to the returned action; these are popped here (never reach
the agent) and recorded in the step. tok_probe() -> (calls, pt, ct) cumulative snapshot
for per-step token deltas (optional).
"""
from __future__ import annotations

from bench_v3.config.constants import MAX_ACTIONS, TERMINAL_ACTIONS
from bench_v3.core.observation import visible_observation, redact_action
from bench_v3.core.verifier import verify
from bench_v3.core.simulator import BenchSimulator, true_in_tol
from bench_v3.core.transcript import EpisodeResult


def run_episode(policy, sim: BenchSimulator, *, tok_probe=None) -> EpisodeResult:
    action_log: list = []
    committed: list = []
    truth_log: list = []
    steps: list = []
    actions_used = 0
    calls = 0
    parse_fails = 0
    terminal = None

    def _tok():
        return tok_probe() if tok_probe else (0, 0, 0)

    while actions_used < MAX_ACTIONS:
        tok0 = _tok()
        obs = visible_observation(sim, action_log, actions_used)
        action = policy(obs); calls += 1
        if action is None:                                   # [G7] one free parse retry
            action = policy(obs, retry=True); calls += 1
            if action is None:
                parse_fails += 1
                actions_used += 1                            # 2nd failure costs budget
                action_log.append({"action": None, "committed": False,
                                   "verifier": {"reason": "unparseable"}})
                t1 = _tok()
                steps.append({"step": actions_used, "action": None, "committed": False,
                              "verifier": {"reason": "unparseable"}, "result": None,
                              "tib": None, "tia": None, "stock_accurate": None,
                              "critic": None, "proposals": None,
                              "tok": {"calls": t1[0] - tok0[0], "pt": t1[1] - tok0[1], "ct": t1[2] - tok0[2]}})
                continue
        # eval-only audit records (critic / multi-proposal arms attach them; popped so they never reach obs)
        cinfo = action.pop("_critic", None) if isinstance(action, dict) else None
        pinfo = action.pop("_proposals", None) if isinstance(action, dict) else None
        ok, verdict = verify(sim, action)
        if not ok:
            actions_used += 1                                # [G6] rejected costs budget
            action_log.append({"action": redact_action(action), "committed": False, "verifier": verdict})
            t1 = _tok()
            steps.append({"step": actions_used, "action": action, "committed": False,
                          "verifier": verdict, "result": None, "tib": true_in_tol(sim),
                          "tia": None, "stock_accurate": None, "critic": cinfo, "proposals": pinfo,
                          "tok": {"calls": t1[0] - tok0[0], "pt": t1[1] - tok0[1], "ct": t1[2] - tok0[2]}})
            continue
        tib = true_in_tol(sim)
        result = sim.apply(action, inject_fault=False, draw_noise=True)
        tia = true_in_tol(sim)
        actions_used += 1
        committed.append(action["type"])
        stock_acc = None
        if action["type"] == "quarantine_stock":
            s = sim.state.stocks.get(action.get("stock"))
            stock_acc = (s is not None and abs(s.get_true_concentration_M() - s.label_concentration_M) <= 1e-6)
        truth_log.append({"type": action["type"], "tib": tib, "tia": tia, "stock_accurate": stock_acc})
        action_log.append({"action": redact_action(action), "committed": True,
                           "verifier": verdict, "result": result})
        t1 = _tok()
        steps.append({"step": actions_used, "action": action, "committed": True,
                      "verifier": verdict, "result": result, "tib": tib, "tia": tia,
                      "stock_accurate": stock_acc, "critic": cinfo, "proposals": pinfo,
                      "tok": {"calls": t1[0] - tok0[0], "pt": t1[1] - tok0[1], "ct": t1[2] - tok0[2]}})
        if action["type"] in TERMINAL_ACTIONS:
            terminal = action["type"]
            break
    return EpisodeResult(terminal=terminal, actions_used=actions_used, action_log=action_log,
                         committed_types=committed, sim=sim, calls=calls, parse_fails=parse_fails,
                         truth_log=truth_log, steps=steps)
