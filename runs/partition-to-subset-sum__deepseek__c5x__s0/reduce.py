"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

Reduction:
  Let S = sum(numbers).
  * If S is odd, no partition exists.  We emit target = -1, which is
    always a "no" instance of Subset Sum (t < 0 is always no).
  * If S is even, a partition into two equal-sum groups exists iff some
    subset of the numbers sums to exactly S/2 (the complement then sums
    to S - S/2 = S/2).  We emit target = S/2.

The transformation only reads the numbers and computes their sum, so it
runs in O(n) time (polynomial).  It never calls a solver.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        # Odd total: Partition is always "no".  Subset Sum with a
        # negative target is always "no" as well.
        target = -1
    else:
        target = total // 2
    return {"numbers": list(numbers), "target": target}
