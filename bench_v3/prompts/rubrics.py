"""Rubrics: L2 (main) + D1 ablation variants (L1 / L3 / GENERIC). Verbatim materials v1.4."""

L2 = """

Operating principles:
1. Measure before you act. Never apply a corrective action based only on records.
2. Before any corrective or terminal action, verify the instrument once against a reference standard.
3. A surprising reading has several possible causes. The delivered amount could be wrong, the instrument could be wrong, or the stock could differ from its label. Rule them out with evidence instead of assuming the first explanation.
4. When records and verified measurements disagree, trust the measurements.
5. Compute corrections from mass balance and aim to reach the target in one corrective step.
6. If no in-vessel correction can reach the target, discard and rebuild instead of forcing a fix.
7. Do not alter a healthy system. Never recalibrate, quarantine, or discard anything the evidence shows is fine.
8. When verified evidence shows the goal is met, accept. Do not spend budget seeking more certainty than the tolerance requires.
9. Keep one action in reserve to confirm or close out. Never end with the situation unresolved."""

L1 = """

Operating principles:
1. Gather sufficient evidence before acting.
2. Consider alternative explanations before committing to one.
3. Prefer reversible steps while uncertain.
4. Act decisively once the evidence is clear.
5. Leave the situation in a safe and accounted state."""

L3 = """

Procedure:
1. Measure the vessel concentration, then measure the high reference standard.
2. If the standard reading is off, the instrument is at fault. Recalibrate using both standards, then accept the batch.
3. If the standard reading is correct and the vessel is below target, add stock to reach the target, then accept.
4. If the standard reading is correct and the vessel is above target, add solvent up to the computed volume, then accept.
5. If no single in-vessel addition can reach the target within capacity, discard the vessel, transfer fresh stock, dilute to target, then accept.
6. If the measurement conflicts with label arithmetic, compute the true stock concentration from the measurement and use it for all corrections."""

GENERIC = """

Operating principles:
1. Wear appropriate protective equipment at all times in the laboratory.
2. Label every container clearly and include the date of preparation.
3. Keep the work area clean and free of unnecessary clutter.
4. Know the location of all safety equipment before starting any procedure.
5. Never work alone when handling hazardous materials.
6. Dispose of chemical waste only in the designated containers.
7. Report every incident and near miss to the supervisor promptly.
8. Wash hands thoroughly before leaving the laboratory.
9. Review the safety data sheet before using an unfamiliar substance."""
