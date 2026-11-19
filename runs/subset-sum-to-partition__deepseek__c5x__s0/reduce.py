"""Polynomial-time reduction from Subset Sum to Partition.

Source (Subset Sum): {"numbers": [a1, ...], "target": t}
Target (Partition):  {"numbers": [a1, ...]}

Idea
----
Let S = sum(numbers).  A subset of the source numbers sums to t iff its
complement sums to S - t.  So we may assume the (effective) target t' satisfies
t' <= S/2 by replacing t with S - t when t > S/2.  Then b = S - 2*t' >= 0.

Map the source instance to the Partition instance

    {"numbers": numbers + [b]}.

Its total is S + b = 2*(S - t'), so a valid partition is exactly a subset of
the augmented list summing to S - t'.  Such a subset either omits b (then the
original part sums to S - t') or includes b (then the original part sums to
t').  Both conditions are equivalent to the existence of a source subset
summing to t' (complement symmetry), hence to a source subset summing to t.

Trivial cases are mapped to fixed yes/no Partition instances:
  * t < 0  -> no  (no subset of non-negative numbers sums to a negative value)
  * t > S  -> no  (no subset sums to more than the total)
  * t == 0 -> yes (the empty sub-list)
"""

from __future__ import annotations

from typing import Any

# Fixed target instances used for the trivially-yes / trivially-no cases.
_YES_INSTANCE = {"numbers": []}          # empty list partitions into two empty groups
_NO_INSTANCE = {"numbers": [1]}          # total 1 is odd -> never partitionable


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Subset Sum instance to a Partition instance."""
    numbers = list(instance["numbers"])
    target = instance["target"]

    # Trivial no cases.
    if target < 0:
        return dict(_NO_INSTANCE)

    total = sum(numbers)

    if target > total:
        return dict(_NO_INSTANCE)

    # Trivial yes case: the empty sub-list sums to 0.
    if target == 0:
        return dict(_YES_INSTANCE)

    # Use complement symmetry so that the effective target is at most total/2.
    effective = target if target <= total - target else total - target

    # effective <= total/2, so this is non-negative.
    b = total - 2 * effective

    return {"numbers": numbers + [b]}
