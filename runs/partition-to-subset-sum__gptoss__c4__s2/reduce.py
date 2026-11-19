"""Reduction from Partition to Subset Sum.

The source problem is :class:`Partition` defined in ``problems.py``.
The target problem is :class:`SubsetSum` defined in the same file.

Given an instance ``{"numbers": [a1, a2, ...]}`` we produce an instance of
Subset Sum such that the answer (yes/no) is preserved.

Standard reduction:
    * Let ``S`` be the sum of all numbers.
    * If ``S`` is even, we ask whether a subset sums to ``S // 2`` – this is
      exactly the partition condition.
    * If ``S`` is odd, the Partition instance is a definite *no*.  We can
      produce any Subset‑Sum instance that is also a definite *no*.  The
      specification guarantees that a negative target is always a *no*
      instance, regardless of the numbers.  Therefore we return an empty
      list with target ``-1``.

The reduction runs in linear time in the size of the input and uses only
integer arithmetic, satisfying the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import Partition, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to the ``Partition`` format, i.e.
        ``{"numbers": [...]}`` where the list contains non‑negative ints.

    Returns
    -------
    dict
        A valid ``SubsetSum`` instance preserving the answer.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if
    # the input is malformed, matching the behaviour expected from a reduction.
    Partition.validate(instance)

    numbers: List[int] = instance["numbers"]
    total = sum(numbers)

    if total % 2 == 1:
        # Odd total → Partition is a guaranteed NO.  Use a negative target
        # which is a guaranteed NO for Subset Sum.
        reduced = {"numbers": [], "target": -1}
    else:
        target = total // 2
        reduced = {"numbers": numbers.copy(), "target": target}

    # Ensure the produced instance is valid for the target problem.
    SubsetSum.validate(reduced)
    return reduced

