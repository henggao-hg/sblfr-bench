# Complex Fault Design (Planned)

These compound and time-dependent fault types are designed for a held-out
generalization test. They are not part of the frozen Tier-1 benchmark and are
documented here as planned extensions. Each fault keeps the same observation
schema, the same 12 actions, and the same budget of 8 actions as Tier-1, so an
agent cannot tell whether an instance is standard or held-out.

## 1. Compound fault: transfer error and instrument bias together

A transfer volume error and an instrument reading bias are injected at the same
time. Each component is individually detectable, meaning each one shifts the
reading by at least the tolerance plus three standard deviations. This breaks the
assumption that only one fault is present, so a single-cause diagnosis is no
longer correct. Two difficulty levels are used. In the mild level, the chemistry
can be corrected in a single step after recalibration and the goal can still be
met within the budget. In the severe level, the batch needs to be rebuilt after
recalibration and cannot be fixed within the budget, so the correct outcome is a
safe handoff with the instrument already recalibrated.

## 2. Temporal drift: instrument bias grows over time

The instrument bias increases with the number of actions taken, so the reading
drifts as the episode proceeds. Repeating the same standard measurement at
different steps reveals that the reading moves over time. Recalibration does not
help because the instrument keeps drifting. The correct behavior is to recognize
the instability and hand off, rather than accept a batch based on a temporarily
normal reading.

## 3. Slow evaporation: vessel volume decreases over time

The true volume of the vessel decreases by a small fraction at each step, so the
concentration rises over time. As with drift, the evidence is in the trend across
measurements, but here the fault is on the chemistry side rather than the
instrument. The batch can usually be corrected within the budget by adding a
small amount of solvent once the trend is recognized.
