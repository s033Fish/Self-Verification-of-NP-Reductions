"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance: {"numbers": [a1, a2, ...]}
Subset Sum instance: {"numbers": [a1, a2, ...], "target": t}

A Partition instance is yes exactly when the total sum is even and some
sub-list sums to half the total.  So:

  * If the total is even, use the same numbers with target = total // 2.
    A subset summing to total // 2 is exactly one of the two equal-sum
    groups (the complement is the other group).

  * If the total is odd, Partition is always no.  Use target = -1, which
    Subset Sum always answers no (t < 0 is always no).

Both cases are computed in time linear in the size of the input, so the
reduction runs in polynomial time and never calls a brute-force solver.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Partition instance to a Subset Sum instance.

    The returned instance is yes for Subset Sum exactly when ``instance``
    is yes for Partition.
    """
    numbers = list(instance["numbers"])
    total = sum(numbers)

    if total % 2 == 0:
        target = total // 2
    else:
        # Odd total: Partition is always no, so pick an always-no target.
        target = -1

    return {"numbers": numbers, "target": target}
