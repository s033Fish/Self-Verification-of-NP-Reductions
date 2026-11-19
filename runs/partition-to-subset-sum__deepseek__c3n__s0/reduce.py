"""Polynomial-time reduction from Partition to Subset Sum.

SOURCE = Partition:   {"numbers": [a1, a2, ...]}
TARGET = Subset Sum:  {"numbers": [a1, a2, ...], "target": t}

Partition is yes iff the positions can be split into two groups of equal
sum.  Let S = sum(numbers).  A valid split exists iff some subset of the
numbers sums to exactly S/2 (the complement then sums to S/2 as well).

* If S is even, the target instance uses the same numbers with target S//2.
  Any subset summing to S//2 gives a partition (take that subset and its
  complement); conversely any partition yields such a subset.
* If S is odd, no subset can sum to S/2, so Partition is no.  We emit a
  target that is unreachable: S + 1 (strictly larger than the sum of all
  numbers).  Subset Sum is then no as well.

The construction is O(n) arithmetic operations, hence polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Reduce a Partition instance to a Subset Sum instance."""
    numbers = list(instance["numbers"])
    total = sum(numbers)

    if total % 2 == 1:
        # Partition is always no for an odd total; S + 1 exceeds the sum of
        # all numbers, so no sub-list can reach it.
        target = total + 1
    else:
        target = total // 2

    return {"numbers": numbers, "target": target}
