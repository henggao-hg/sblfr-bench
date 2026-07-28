"""All 11 classes: dispatch sampling + membership to the per-family modules.

sample_instance(family, fault_class, rng) -> BenchInstance (params + injected fault,
started_in_tol filled). certify_membership(inst) -> bool. Faithful to bench_v2
instances.sample_instance / certify_membership, split by family.
"""
from __future__ import annotations
import random

from bench_v3.config.constants import CLASSES
from bench_v3.families.base import BenchInstance, base_params, true_post_protocol_conc
from bench_v3.families import f1_transfer, f2_instrument, f3_reagent

_FAMILY_MOD = {"f1": f1_transfer, "f2": f2_instrument, "f3": f3_reagent}


def sample_instance(family: str, fault_class: str, rng: random.Random) -> BenchInstance:
    kw = dict(id="", family=family, fault_class=fault_class, **base_params(rng))
    _FAMILY_MOD[family].sample(fault_class, rng, kw)
    inst = BenchInstance(**kw)
    inst.started_in_tol = abs(true_post_protocol_conc(inst) - inst.target_concentration_M) <= inst.tolerance_M
    return inst


def certify_membership(inst: BenchInstance) -> bool:
    return _FAMILY_MOD[inst.family].membership(inst)


def all_class_specs():
    """Yield (family, fault_class) for the 11 classes."""
    for fam, classes in CLASSES.items():
        for fc in classes:
            yield fam, fc
