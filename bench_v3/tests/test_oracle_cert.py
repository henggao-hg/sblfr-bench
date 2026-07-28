"""oracle + battery gate (fast, on a small library). Full 275 freeze is run via
scripts/freeze_library.py. Here: every class fills under dual cert, every kept instance
solves in <= 7 steps, and the 5 degenerate strategies all trip the registered gate.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench_v3.config.constants import CLASSES, ORACLE_MAX_STEPS
from bench_v3.instances.generate import generate_library
from bench_v3.instances.battery import run_battery, gate_passes, check_caps


def test_oracle_cert_and_battery_small():
    lib, stats = generate_library(n_per_class=3, seed=42, verbose=False)
    n_classes = sum(len(v) for v in CLASSES.values())
    assert len(lib) == n_classes * 3, f"library {len(lib)} != {n_classes*3}"
    for key, s in stats.items():
        assert s["kept"] == 3, f"{key} only filled {s['kept']}/3"
        assert s["max_steps"] is not None and s["max_steps"] <= ORACLE_MAX_STEPS, f"{key} max_steps={s['max_steps']} > {ORACLE_MAX_STEPS}"
    print(f"[PASS] all {n_classes} classes fill 3/3 under dual cert; every kept instance solves in <= {ORACLE_MAX_STEPS} steps")
    print("       (cert keeps only certified instances -> 0 oracle fail by construction)")

    res = run_battery(lib, verbose=True)
    caps_ok = check_caps(res, lib, verbose=True)
    gate_ok = gate_passes(res, verbose=True)
    assert gate_ok, "battery gate FAILED"
    assert caps_ok, "battery analytic cap EXCEEDED"
    print("[PASS] battery: five degenerate strategies all trip the registered gate; caps hold")


if __name__ == "__main__":
    test_oracle_cert_and_battery_small()
    print("\nORACLE CERT + BATTERY (small) PASSED")
