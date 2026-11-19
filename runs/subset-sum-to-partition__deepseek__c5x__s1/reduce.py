"""Polynomial-time reduction from Subset Sum to Partition.

Source instance : {"numbers": [a1, ...], "target": t}
Target instance : {"numbers": [b1, ...]}

Idea
----
Let S = sum(numbers).

* t < 0 : Subset Sum is always NO.  Return [1] (odd total -> Partition NO).
* t = 0 : Subset Sum is always YES. Return [] (empty list -> Partition YES).
* t > S : impossible, always NO.    Return [1].
* otherwise let t' = min(t, S - t).  A subset of the numbers sums to t iff
  some subset sums to t' (take complements when t' = S - t).  Now t' <= S/2,
  so b = S - 2*t' >= 0.  Output numbers + [b].  The total is
      2*S - 2*t' = 2*(S - t'),
  so a partition exists iff some subset of numbers + [b] sums to S - t'.
  A subset containing b has the rest summing to t'; a subset not containing b
  has complement summing to t'.  Hence Partition is YES iff a subset of the
  original numbers sums to t', i.e. iff Subset Sum is YES.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = list(instance["numbers"])
    target = instance["target"]

    if target < 0:
        return {"numbers": [1]}
    if target == 0:
        return {"numbers": []}

    total = sum(numbers)
    if target > total:
        return {"numbers": [1]}

    t = min(target, total - target)
    extra = total - 2 * t
    return {"numbers": numbers + [extra]}
