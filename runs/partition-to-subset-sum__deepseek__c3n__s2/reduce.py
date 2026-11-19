"""Polynomial-time reduction from Partition to Subset Sum.

Partition instance:  {"numbers": [a1, a2, ...]}
SubsetSum instance:  {"numbers": [a1, a2, ...], "target": t}

A Partition instance is yes exactly when some sub-list of its numbers sums to
half of the total sum.  So we let t = total // 2 when the total is even.

When the total is odd, Partition is always no; we emit a target that Subset
Sum can never meet (a negative target is always no), so the answer stays no.

The construction only sums the numbers and copies the list, so it runs in
linear time (polynomial).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 == 1:
        # Odd total: Partition is definitely no.  Use a negative target,
        # which Subset Sum always answers no.
        target = -1
    else:
        target = total // 2
    return {"numbers": list(numbers), "target": target}
