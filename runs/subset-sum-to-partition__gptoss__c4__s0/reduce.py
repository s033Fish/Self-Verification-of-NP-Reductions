"""Reduction from Subset Sum to Partition.

The source problem (SubsetSum) instance format is:
    {"numbers": [a1, a2, ...], "target": t}
The target problem (Partition) instance format is:
    {"numbers": [b1, b2, ...]}

We implement the classic polynomial‑time reduction:

* Let S be the list of numbers and let T be the target.
* Let total = sum(S).
* If T < 0 or T > total, the Subset‑Sum instance is a definite "no".
  In this case we return a Partition instance that is also a definite "no"
  (e.g., a single odd number).
* Otherwise (0 ≤ T ≤ total) we may replace T by the smaller of T and
  total‑T (the complement subset sum) to ensure the extra element is
  non‑negative.  Let effective_target = min(T, total‑T) and set
  extra = total - 2*effective_target (which is ≥ 0).  Adding `extra` to the
  list yields a Partition instance that is a yes exactly when the original
  Subset‑Sum instance is a yes.

The reduction runs in linear time and respects the non‑negative integer
requirement of the Partition problem.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SubsetSum, Partition


def reduce(instance: Dict) -> Dict:
    """Reduce a SubsetSum instance to a Partition instance.

    Parameters
    ----------
    instance: dict
        A validated SubsetSum instance.

    Returns
    -------
    dict
        A validated Partition instance with the same answer.
    """
    # Validate the source instance – will raise if malformed.
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])
    target: int = int(instance["target"])
    total = sum(numbers)

    # Cases where the Subset‑Sum answer is definitively NO.
    if target < 0 or target > total:
        # Return a Partition instance that is definitely NO: a single odd number.
        partition_instance = {"numbers": [1]}
        Partition.validate(partition_instance)
        return partition_instance

    # Otherwise 0 <= target <= total.
    # Use the smaller of target and its complement to keep extra non‑negative.
    effective_target = target if target <= total - target else total - target
    extra = total - 2 * effective_target  # guaranteed >= 0
    new_numbers = numbers + [extra]
    partition_instance = {"numbers": new_numbers}
    Partition.validate(partition_instance)
    return partition_instance

