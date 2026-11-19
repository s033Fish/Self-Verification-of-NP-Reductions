"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

A Partition instance is yes iff some sub-list of its numbers sums to
half of the total sum (the other half is the complement).  So we simply
ask Subset Sum for target = total // 2.

If the total is odd, no such split exists, so we map to an impossible
Subset Sum instance by choosing a negative target (t < 0 is always no).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 == 1:
        target = -1  # odd total: Partition is always no, t < 0 is always no
    else:
        target = total // 2
    return {"numbers": numbers, "target": target}
