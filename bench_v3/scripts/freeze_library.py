"""Generate + freeze the full library_v3.json (275 = 11 classes x 25). Pure scripted ($0).
usage: python -m bench_v3.scripts.freeze_library
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench_v3.instances.generate import generate_library, freeze, LIBRARY_PATH

if __name__ == "__main__":
    lib, stats = generate_library(verbose=True)
    freeze(lib)
    bad = [k for k, s in stats.items() if s["kept"] != 25 or (s["max_steps"] or 99) > 7]
    print(f"\nfroze {len(lib)} instances to {LIBRARY_PATH}")
    print("ALL CLASSES 25 + steps<=7" if not bad else f"PROBLEM classes: {bad}")
