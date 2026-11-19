"""Reduction from Partition to Subset Sum.

The source problem is :class:`Partition` (defined in ``problems.py``).
The target problem is :class:`SubsetSum` (also defined in ``problems.py``).

For an instance ``I`` of Partition we construct an instance ``J`` of
SubsetSum such that ``I`` is a yes‑instance iff ``J`` is a yes‑instance.

Standard reduction:
    * Let ``numbers`` be the list of non‑negative integers from the
      Partition instance.
    * Let ``S = sum(numbers)``.
    * If ``S`` is even, we ask the SubsetSum instance whether a subset
      sums to ``S // 2`` – this is exactly the Partition condition.
    * If ``S`` is odd, the Partition instance is a definite *no*.
      To preserve the answer we choose a target larger than the total
      sum (``S + 1``).  Because all numbers are non‑negative, no subset
      can reach that target, so the SubsetSum instance is also a *no*.

The reduction runs in linear time in the size of the input list and
therefore satisfies the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import Partition, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to the Partition instance format.

    Returns
    -------
    dict
        A dictionary that conforms to the SubsetSum instance format.
    """
    # Validate the source instance – this will raise ``InvalidInstance``
    # if the input is malformed.
    Partition.validate(instance)

    numbers: List[int] = list(instance["numbers"])  # copy to avoid side‑effects
    total = sum(numbers)

    if total % 2 == 0:
        # Even total: ask for exactly half of the sum.
        target = total // 2
    else:
        # Odd total: the Partition instance is a definite NO.  Choose a
        # target greater than any achievable sum so the SubsetSum instance
        # is also a NO.
        target = total + 1

    # Construct the SubsetSum instance.
    return {"numbers": numbers, "target": target}

