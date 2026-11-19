"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

A Partition instance is yes iff the total sum S is even and some subset of
the numbers sums to S/2 (the complement then sums to S/2 as well).  So:

  * If S is even, return {"numbers": numbers, "target": S // 2}.
  * If S is odd, the answer is always no; return an instance that is
    always no, e.g. {"numbers": [], "target": -1} (t < 0 is always no).

Runs in O(n) time (just summing the numbers).
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 == 1:
        # Odd total: Partition is always no.  t < 0 is always no.
        return {"numbers": [], "target": -1}
    return {"numbers": list(numbers), "target": total // 2}
