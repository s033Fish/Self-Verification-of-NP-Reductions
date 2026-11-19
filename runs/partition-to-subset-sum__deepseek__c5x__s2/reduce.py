"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

Reduction:
  Let S = sum(numbers).
  - If S is odd, no partition into two equal-sum groups can exist, so we
    emit a Subset Sum instance that is guaranteed "no": target = -1
    (t < 0 is always no).
  - If S is even, a partition exists iff some sub-list sums to S/2, so we
    emit the same numbers with target = S // 2.

This is clearly polynomial time (one summation) and does not call any
brute-force solver.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 != 0:
        # Odd total: Partition is always no. Use target < 0, always no.
        target = -1
    else:
        target = total // 2
    return {"numbers": numbers, "target": target}
