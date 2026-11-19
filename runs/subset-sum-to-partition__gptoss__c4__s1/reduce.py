"""Reduction from Subset Sum to Partition.

We transform a Subset‑Sum instance (A, t) into a Partition instance B such that
B has a valid partition iff A contains a subset summing to t.

Construction (for 0 < t ≤ S where S = sum(A)):
    B = A ∪ { x, y } where
        x = 2·S - t
        y = S + t
The total sum of B is 4·S, so each side of a partition must sum to 2·S.
Because y > S, any subset achieving sum 2·S must contain x and may contain a
subset of A that sums to t; it cannot contain y (otherwise the sum would exceed
2·S). Hence a partition exists ⇔ a subset of A sums to t.

Edge cases:
* t = 0 → Subset‑Sum is always yes. We map to the empty list, which is a
  trivially yes instance for Partition.
* t < 0 or t > S → Subset‑Sum is a definite no. We map to a single odd element
  [1]; its total sum is odd, so Partition is a no instance.

Both mappings use only non‑negative integers and run in linear time.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import SubsetSum, Partition


def reduce(instance: Dict[str, Any]) -> Dict[str, List[int]]:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the SubsetSum format.

    Returns
    -------
    dict
        A Partition instance with the same yes/no answer as the input.
    """
    # Validate source instance.
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])  # shallow copy
    target: int = instance["target"]
    total = sum(numbers)

    # Edge cases.
    if target == 0:
        # Always yes for Subset‑Sum → empty Partition instance (yes).
        part_instance = {"numbers": []}
        Partition.validate(part_instance)
        return part_instance
    if target < 0 or target > total:
        # Always no → odd total Partition instance (no).
        part_instance = {"numbers": [1]}
        Partition.validate(part_instance)
        return part_instance

    # Normal case: 0 < target <= total.
    x = 2 * total - target
    y = total + target
    new_numbers = numbers + [x, y]
    part_instance = {"numbers": new_numbers}
    Partition.validate(part_instance)
    return part_instance

