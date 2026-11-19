"""Polynomial-time reduction from Subset Sum to Partition.

Source instance: {"numbers": [a1, a2, ...], "target": t}
Target instance: {"numbers": [b1, b2, ...]}

Reduction
---------
Let S = sum(numbers).

* If t < 0 or t > S the Subset Sum answer is no.  Return the trivially
  no Partition instance {"numbers": [1]} (odd total).

* Otherwise add the single extra number b = |S - 2t| and return
  {"numbers": numbers + [b]}.

Why it works
------------
The returned list has total S + |S - 2t| = 2 * max(t, S - t), so the
required equal half-sum is h = max(t, S - t).

If t <= S/2 then b = S - 2t and h = S - t.  A subset R of the original
numbers sums to t iff R together with b sums to t + (S - 2t) = S - t = h.
Conversely, any half summing to h either uses b (leaving original numbers
summing to t) or does not (its complement among the originals sums to t).

If t > S/2 then b = 2t - S and h = t.  A subset R of the originals sums
to t iff R is itself a half; conversely any half either avoids b (giving a
subset summing to t) or uses b (whose complement among the originals sums
to S - (t - b) = t).

Thus the Partition instance is yes exactly when the Subset Sum instance
is yes.  The construction takes linear time.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Subset Sum instance to a Partition instance."""
    numbers = list(instance["numbers"])
    target = instance["target"]
    total = sum(numbers)

    # Negative targets and targets above the total are always no.
    if target < 0 or target > total:
        return {"numbers": [1]}

    extra = abs(total - 2 * target)
    return {"numbers": numbers + [extra]}
