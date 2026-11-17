"""Polynomial-time reduction from Subset Sum to Partition.

Source (SubsetSum): {"numbers": [a1, a2, ...], "target": t}
  numbers are non-negative ints, t is any int.
  Yes iff some sub-list sums to exactly t.

Target (Partition): {"numbers": [a1, a2, ...]}
  numbers are non-negative ints.
  Yes iff positions can be split into two groups of equal sum.

Reduction:
  Let S = sum(numbers).
  * t < 0             -> Subset Sum is always no.
                         Return [1] (odd total => Partition no).
  * t == 0            -> Subset Sum is always yes.
                         Return [] (empty list => Partition yes).
  * t > S             -> no subset can reach t, so no.
                         Return [1] (odd total => Partition no).
  * 1 <= t <= S       -> let t' = t if 2t <= S else S - t.
                         (A subset sums to t iff its complement sums to
                         S - t, so this preserves the answer and makes
                         S - 2t' >= 0.)
                         Return numbers + [S - 2t'].
                         New total = 2(S - t'), half = S - t'.
                         A subset of the new multiset sums to S - t' iff
                         either it contains the extra element S - 2t' and
                         the rest sums to t', or it omits it and its
                         complement among the original numbers sums to t'.
                         Hence Partition is yes exactly when Subset Sum is.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = list(instance["numbers"])
    t = instance["target"]

    # t < 0: Subset Sum is always no; [1] has odd total so Partition is no.
    if t < 0:
        return {"numbers": [1]}

    # t == 0: Subset Sum is always yes (empty sub-list); [] is Partition-yes.
    if t == 0:
        return {"numbers": []}

    total = sum(numbers)

    # t > total: impossible, so Subset Sum is no; [1] is Partition-no.
    if t > total:
        return {"numbers": [1]}

    # 1 <= t <= total.  If t > total/2, solve the complementary target
    # total - t (a subset sums to t iff its complement sums to total - t).
    if 2 * t > total:
        t = total - t

    extra = total - 2 * t  # >= 0 by construction
    return {"numbers": numbers + [extra]}
