"""Polynomial-time reduction from Partition to Subset Sum.

SOURCE = Partition:  {"numbers": [a1, a2, ...]}
TARGET = SubsetSum:  {"numbers": [a1, a2, ...], "target": t}

Reduction:
    Let S = sum(numbers).

    * If S is even, output {"numbers": numbers, "target": S // 2}.
      A partition into two equal-sum groups exists iff some subset of the
      numbers sums to exactly S/2 (the subset is one group; its complement
      is the other group, and it automatically sums to S - S/2 = S/2).

    * If S is odd, no partition exists (two equal integer sums would make
      the total even).  Output {"numbers": numbers, "target": S + 1}.
      Every sub-list sums to at most S < S + 1, so the target instance is
      a definite "no".

The reduction runs in time linear in the size of the input (one sum and
one integer division), hence polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Partition instance to a Subset Sum instance.

    The returned instance is a yes-instance of Subset Sum exactly when the
    input is a yes-instance of Partition.
    """
    numbers = list(instance["numbers"])
    total = sum(numbers)

    if total % 2 == 0:
        target = total // 2
    else:
        # Odd total: Partition is definitely "no".  Use an unreachable
        # target (all numbers are non-negative, so no sub-list can exceed
        # the total sum).
        target = total + 1

    return {"numbers": numbers, "target": target}
