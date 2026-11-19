"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

A partition into two equal-sum groups exists iff the total sum S is even
and some sub-list sums to S/2 (the complement then sums to S/2 as well).
So:
  * S odd  -> answer is no; return target = -1 (Subset Sum is always no for
              a negative target, regardless of the numbers).
  * S even -> return the same numbers with target = S/2.

The transformation only computes the sum, so it runs in O(n) time.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Partition instance to a Subset Sum instance.

    The returned instance is yes exactly when the input is yes.
    """
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 == 1:
        # Odd total: Partition is always no.  Use a negative target, which
        # Subset Sum answers no for every list (including the empty list).
        return {"numbers": numbers, "target": -1}
    return {"numbers": numbers, "target": total // 2}
