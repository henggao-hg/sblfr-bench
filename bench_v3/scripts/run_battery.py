"""Run the degenerate-strategy battery on the frozen library + check gate/caps.
usage: python -m bench_v3.scripts.run_battery
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench_v3.instances.generate import load_library
from bench_v3.instances.battery import run_battery, check_caps, gate_passes

if __name__ == "__main__":
    lib = load_library()
    print(f"battery on {len(lib)} instances:")
    res = run_battery(lib, verbose=True)
    caps_ok = check_caps(res, lib, verbose=True)
    gate_ok = gate_passes(res, verbose=True)
    print("\nBATTERY SIGNED OFF" if (gate_ok and caps_ok) else "\nBATTERY FAILED")
