"""Polynomial-time reduction from Subset Sum to Partition.

Source instance:  {"numbers": [a1, ..., an], "target": t}   (a_i >= 0, t any int)
Target instance:  {"numbers": [b1, ..., bm]}                (b_j >= 0)

Idea
----
Let S = sum(numbers).

* If t < 0 or t > S the answer is "no".  Emit [1] (odd total -> always no).
* Otherwise a subset of the numbers sums to t iff a subset sums to
  t' = min(t, S - t)  (complementing a subset swaps t and S - t, and
  t' <= S/2 so it is the "small" side).
  Add one extra number b = S - 2*t' >= 0.  The new total is
       S + b = 2*(S - t'),
  so a perfect partition must pick a sub-list summing to S - t'.
  A sub-list of the extended list summing to S - t' either
    - contains b, and then the rest of the numbers sum to
      (S - t') - (S - 2t') = t', or
    - does not contain b, and then its complement (within the original
      numbers) sums to S - (S - t') = t'.
  Conversely any sub-list of the original numbers summing to t' extends to
  one summing to S - t' (add b if needed / take its complement).
  Hence the partition instance is yes iff the subset-sum instance is yes.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = list(instance["numbers"])
    target = instance["target"]
    total = sum(numbers)

    # Infeasible targets: always "no".  [1] has odd total, so Partition is "no".
    if target < 0 or target > total:
        return {"numbers": [1]}

    # Work with the smaller of target and total - target (complement symmetry).
    t = min(target, total - target)
    extra = total - 2 * t  # >= 0 because t <= total / 2
    return {"numbers": numbers + [extra]}
