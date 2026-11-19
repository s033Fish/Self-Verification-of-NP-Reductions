"""Polynomial-time reduction from Subset Sum to Partition.

Source instance:  {"numbers": [a1, ...], "target": t}
Target instance:  {"numbers": [b1, ...]}

Reduction: let S = sum(numbers) and add one extra number
    e = |S - 2t|.
Then the augmented list can be partitioned into two equal-sum groups iff
the original numbers contain a sub-list summing to exactly t.

Proof sketch (T = S + e = 2*max(S,t) is the new total, so each group must
sum to max(S, t)):
  * If a sub-list A sums to t, its complement in the original list sums to
    S - t, and one of {A, complement, complement+extra} gives a group of
    sum max(S, t) depending on whether S >= t.
  * Conversely any group of sum max(S, t) either avoids the extra element
    (then it or its complement is an original sub-list summing to t) or uses
    it (then the remaining original elements sum to t).
The extra element is non-negative, so the result is a valid Partition
instance.  Runtime is linear in the input size.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    numbers = list(instance["numbers"])
    target = instance["target"]
    total = sum(numbers)
    extra = abs(total - 2 * target)
    return {"numbers": numbers + [extra]}
