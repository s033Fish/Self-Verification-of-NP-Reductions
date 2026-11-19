"""Polynomial-time reduction from Subset Sum to Partition.

Source instance: {"numbers": [a1, ...], "target": t}
Target instance: {"numbers": [a1, ...]}

Reduction:
    Let S = sum(numbers) and b = |S - 2t|.
    Return {"numbers": numbers + [b]}.

Why it works:
    The new total is T = S + b, which is even (both S >= 2t and S < 2t
    cases give T = 2*max(S-t, t)).  A partition of the new multiset into two
    equal halves exists iff a subset of the original numbers sums to t:

    * If S >= 2t: b = S - 2t and each half has sum S - t.  A subset of the
      originals summing to t, together with b, gives t + (S - 2t) = S - t,
      while the complement sums to S - t.  Conversely, in any partition the
      side containing b has original sum (S - t) - b = t.
    * If S < 2t: b = 2t - S and each half has sum t.  The side not
      containing b is a subset of the originals summing to t, and any such
      subset works (the complement plus b sums to (S - t) + (2t - S) = t).
      Conversely, the side not containing b sums to t.

    The same argument covers t = 0 (always yes: b = S, the whole original
    multiset is one half) and t < 0 (always no: a half would need sum
    S - t > S, impossible).

The extra number b is a non-negative integer, so the target instance is
valid.  The reduction runs in linear time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = list(instance["numbers"])
    target = instance["target"]
    total = sum(numbers)
    b = abs(total - 2 * target)
    return {"numbers": numbers + [b]}
