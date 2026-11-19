"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [...]}
Subset Sum instance: {"numbers": [...], "target": t}

Reduction:
  Let S = sum(numbers).
  * If S is odd, Partition is always no.  Return a Subset Sum instance that
    is always no, e.g. target = -1 (t < 0 is always no).
  * If S is even, Partition is yes iff some subset of the numbers sums to
    exactly S/2, so return {"numbers": numbers, "target": S // 2}.

This is clearly polynomial time (one pass to sum the numbers).
"""

from __future__ import annotations


def reduce(instance):
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 != 0:
        # Odd total: Partition is always no.  A negative target makes
        # Subset Sum always no as well.
        return {"numbers": numbers, "target": -1}
    return {"numbers": numbers, "target": total // 2}
