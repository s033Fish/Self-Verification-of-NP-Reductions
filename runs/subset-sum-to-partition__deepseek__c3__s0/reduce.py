"""Polynomial-time reduction from Subset Sum to Partition.

Given a Subset Sum instance with numbers summing to S and target t, add a
single new element of value |S - 2t|.  The resulting list has total

    S + |S - 2t| = 2 * max(t, S - t),

which is always even, so the Partition half-sum is max(t, S - t).

Equivalence:
  * If some sub-list of the originals sums to t, then that sub-list together
    with the new element (when 2t <= S) or its complement (when 2t > S) forms
    one side of a valid partition.
  * Conversely, any partition of the new list yields a sub-list of the
    originals summing to t (or, equivalently, its complement does).

The construction works uniformly for the edge cases t < 0, t = 0, t > S and
the empty list, so no special-casing is required.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Subset Sum instance to a Partition instance."""
    numbers = list(instance["numbers"])
    target = instance["target"]
    total = sum(numbers)
    extra = abs(total - 2 * target)
    return {"numbers": numbers + [extra]}
