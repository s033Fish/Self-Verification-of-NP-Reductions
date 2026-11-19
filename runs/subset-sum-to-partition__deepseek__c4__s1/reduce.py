"""Polynomial-time reduction from Subset Sum to Partition.

Source (Subset Sum): {"numbers": [a1, a2, ...], "target": t}
Target (Partition):  {"numbers": [a1, a2, ...]}

Construction
------------
Let A be the source numbers and S = sum(A).

* t < 0 or t > S: the answer is "no".  Return a Partition instance that is
  certainly "no", e.g. [1] (odd total).
* t == 0: the answer is "yes" (empty sub-list).  Return [] (empty list, yes).
* 0 < t <= S: a subset of A sums to t iff its complement sums to S - t.
  Set t' = min(t, S - t) <= S/2 and c = S - 2*t' >= 0.  Return A + [c].
  The total is S + c = 2*(S - t'), so a balanced partition needs a subset
  summing to S - t'.  Such a subset either contains c (remaining part of A
  sums to t') or does not (a subset of A sums to S - t').  Both t' and
  S - t' are achievable by subsets of A exactly when t is, so the answers
  match.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Subset Sum instance to a Partition instance."""
    numbers = list(instance["numbers"])
    target = instance["target"]

    total = sum(numbers)

    # Definitely "no": target below 0 or above the total sum.
    if target < 0 or target > total:
        return {"numbers": [1]}

    # Definitely "yes": the empty sub-list.
    if target == 0:
        return {"numbers": []}

    # 0 < target <= total.  Use the complement symmetry so that the smaller
    # of target and total - target is at most half the total.
    t = min(target, total - target)
    extra = total - 2 * t  # >= 0
    return {"numbers": numbers + [extra]}
