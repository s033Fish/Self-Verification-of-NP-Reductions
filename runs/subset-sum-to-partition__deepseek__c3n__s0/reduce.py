r"""Polynomial-time reduction from Subset Sum to Partition.

Subset Sum instance: {"numbers": [a1, ...], "target": t}, numbers >= 0.
Partition instance:  {"numbers": [a1, ...]},          numbers >= 0.

Reduction
---------
Let S = sum(numbers).

* If t < 0 or t > S, the Subset Sum answer is "no" (all numbers are
  non-negative, so no sub-list can sum to a negative value or to more than
  the total).  Return the Partition instance {"numbers": [1]}, whose total
  is odd and which is therefore always "no".

* Otherwise 0 <= t <= S.  A sub-list of numbers sums to t if and only if
  its complement sums to S - t, so we may replace t by
  t' = min(t, S - t) <= S / 2 without changing the answer.  Set

      b = S - 2 * t'  >= 0,

  and return the Partition instance {"numbers": numbers + [b]}.
  Its total is S + b = 2 * (S - t'), so a valid partition splits it into
  two groups of sum S - t'.

  Equivalence:
    (=>) If some sub-list X of numbers sums to t', then its complement
         numbers minus X sums to S - t', and X + [b] sums to
         t' + (S - 2 t') = S - t'.  So the partition exists.
    (<=) If a sub-list Y of numbers + [b] sums to S - t', then either
         b is in Y, in which case Y minus {b} is a sub-list of numbers
         summing to (S - t') - (S - 2 t') = t'; or b is not in Y, in which
         case Y is a sub-list of numbers summing to S - t', so its
         complement in numbers sums to t'.  Either way Subset Sum is
         "yes" (for the original target, since t' is t or S - t).

The reduction is polynomial: it only computes S and appends one number.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = list(instance["numbers"])
    target = instance["target"]

    total = sum(numbers)

    # "no" cases: negative target, or target larger than the total.
    if target < 0 or target > total:
        # [1] has odd total, hence Partition is always "no".
        return {"numbers": [1]}

    # A sub-list sums to target iff its complement sums to total - target,
    # so we can use the smaller of the two as the effective target.
    effective = min(target, total - target)

    b = total - 2 * effective  # >= 0 because effective <= total / 2
    return {"numbers": numbers + [b]}
