"""Generate + freeze the instance library. Rejection-sample each class until N members
pass BOTH membership and oracle certification; freeze to JSON. Ported from bench_v2
oracle.generate_library. The frozen library spans all arms/models (paired design).
"""
from __future__ import annotations
import json
import random
from dataclasses import asdict
from pathlib import Path

from bench_v3.config.constants import N_PER_CLASS
from bench_v3.families.base import BenchInstance
from bench_v3.families.registry import sample_instance, certify_membership, all_class_specs
from bench_v3.instances.certify import certify_oracle

LIBRARY_PATH = str(Path(__file__).resolve().parent / "library_v3.json")


def generate_library(n_per_class: int = N_PER_CLASS, seed: int = 42, verbose: bool = True):
    rng = random.Random(seed)
    library = []
    stats = {}
    for fam, fc in all_class_specs():
        kept = 0; tries = 0; steps = []
        while kept < n_per_class and tries < n_per_class * 400:
            tries += 1
            inst = sample_instance(fam, fc, rng)
            if not certify_membership(inst):
                continue
            ok, st = certify_oracle(inst)
            if not ok:
                continue
            inst.id = f"{fam}_{fc}_{kept:02d}"; inst.oracle_steps = st
            library.append(inst); kept += 1; steps.append(st)
        stats[f"{fam}/{fc}"] = {"kept": kept, "tries": tries, "max_steps": max(steps) if steps else None}
        if verbose:
            print(f"  {fam}/{fc:24s} kept {kept}/{n_per_class}  tries={tries}  "
                  f"max_oracle_steps={max(steps) if steps else '-'}", flush=True)
    return library, stats


def freeze(library, path: str = LIBRARY_PATH):
    json.dump([asdict(i) for i in library], open(path, "w"), indent=0)
    return path


def load_library(path: str = LIBRARY_PATH):
    return [BenchInstance(**d) for d in json.load(open(path))]
