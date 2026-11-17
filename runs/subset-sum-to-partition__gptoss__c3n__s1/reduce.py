"""Reduction from Subset Sum to Partition.

The source problem is SubsetSum. An instance is {"numbers": [...], "target": t}.
The target problem is Partition with instance {"numbers": [...]}.

We implement the standard reduction:
* If t < 0 or t > sum(numbers) the Subset‑Sum answer is NO. Return a Partition
  instance with an odd total, e.g., [1], which is always NO.
* Otherwise let S = sum(numbers) and define extra = abs(S - 2*t) (non‑negative).
  Return the list numbers + [extra].

The new total is S + extra = S + |S - 2*t| = 2 * max(t, S - t), which is even.
A partition exists iff there is a subset of the original numbers summing to t.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SubsetSum, Partition


def reduce(instance: Dict) -> Dict:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance: dict
        Must satisfy SubsetSum.validate.

    Returns
    -------
    dict
        A Partition instance with the same yes/no answer.
    """
    SubsetSum.validate(instance)
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Cases where Subset‑Sum is definitely NO.
    if target < 0:
        return {"numbers": [1]}
    total = sum(numbers)
    if target > total:
        return {"numbers": [1]}

    # Normal case: 0 <= target <= total.
    extra = abs(total - 2 * target)  # non‑negative integer
    new_numbers = numbers + [extra]
    Partition.validate({"numbers": new_numbers})
    return {"numbers": new_numbers}

