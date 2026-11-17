"""Polynomial-time reduction from Subset Sum to Partition.

SOURCE (SubsetSum):  {"numbers": [a1, a2, ...], "target": t}
TARGET (Partition):  {"numbers": [a1, a2, ...]}

Reduction
---------
Let S = sum(numbers).  Map the instance to

    {"numbers": numbers + [abs(S - 2 * t)]}

Correctness
-----------
The new total is S + |S - 2t|, which is always even, and half of it is
max(t, S - t).  A subset of the new list sums to max(t, S - t) iff a
subset of the original numbers sums to t:

  * If S >= 2t, the added element is S - 2t and the target half is S - t.
    Taking the added element leaves a subset of the originals summing to t;
    omitting it gives a subset of the originals summing to S - t, whose
    complement sums to t.
  * If S < 2t, the added element is 2t - S and the target half is t.
    Taking the added element requires a subset of the originals summing to
    S - t (equivalent by complement to a subset summing to t); omitting it
    requires a subset of the originals summing to t.

Conversely, any subset of the originals summing to t extends to a valid
half of the new list.  Hence the two instances have the same answer.

The reduction runs in O(n) arithmetic operations (the integers may be
large, but no search over subsets is performed).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Subset Sum instance to a Partition instance."""
    numbers = list(instance["numbers"])
    target = instance["target"]
    total = sum(numbers)
    extra = abs(total - 2 * target)
    return {"numbers": numbers + [extra]}
