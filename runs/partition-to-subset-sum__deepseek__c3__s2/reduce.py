"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]} with non-negative ints.
Subset Sum instance: {"numbers": [...], "target": t}.

Reduction: let S = sum(numbers).
  * If S is even, a partition into two equal-sum groups exists iff some
    sub-list sums to S // 2 (the complement then sums to S // 2 as well).
    So return {"numbers": numbers, "target": S // 2}.
  * If S is odd, no partition exists. Return the same numbers with
    target = S + 1, which exceeds the sum of every sub-list, so the
    Subset Sum instance is a guaranteed "no".

The transformation only computes a sum and an integer division, so it runs
in time linear in the input size (polynomial).
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Partition instance to an equivalent Subset Sum instance."""
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 == 0:
        target = total // 2
    else:
        # Odd total: Partition is always no. Pick a target strictly larger
        # than the sum of all numbers, so no sub-list can reach it.
        target = total + 1
    return {"numbers": numbers, "target": target}
