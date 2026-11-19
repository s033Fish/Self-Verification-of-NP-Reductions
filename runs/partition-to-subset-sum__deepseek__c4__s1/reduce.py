"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

Idea: a partition into two equal-sum groups exists iff some sub-list sums to
half of the total sum (the complement then sums to the other half).

  * If the total is odd, no such sub-list can exist, so we emit an instance
    that is always "no" (target = -1, since t < 0 is always no).
  * Otherwise we emit the same numbers with target = total // 2.

This runs in linear time in the size of the input.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 != 0:
        # Odd total: Partition is always "no"; target < 0 is always "no".
        return {"numbers": numbers, "target": -1}
    return {"numbers": numbers, "target": total // 2}
