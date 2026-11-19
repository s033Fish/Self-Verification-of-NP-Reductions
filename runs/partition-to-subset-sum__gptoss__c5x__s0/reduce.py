"""Reduction from Partition to Subset Sum.

The source problem is :class:`Partition` defined in ``problems.py``.
The target problem is :class:`SubsetSum` defined in the same file.

For an instance ``{"numbers": nums}`` of Partition we construct the
instance ``{"numbers": nums, "target": t}`` of SubsetSum where ``t`` is the
desired half‑sum.  The classic reduction works as follows:

* Let ``S`` be the total sum of ``nums``.
* If ``S`` is odd then the Partition instance is a definite ``NO``.  We map
  it to a SubsetSum instance with a negative target (e.g. ``-1``) because the
  Subset Sum problem is defined to be ``NO`` for any negative target.
* If ``S`` is even we set ``t = S // 2``.  Then a subset of ``nums`` sums to
  ``t`` exactly when the numbers can be split into two groups of equal sum.

The reduction runs in time linear in the size of the input (the sum is
computed in a single pass) and therefore is polynomial.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Partition, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Map a Partition instance to an equivalent SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Partition instance.  It must contain the
        key ``"numbers"`` with a list of non‑negative integers.

    Returns
    -------
    dict
        A dictionary representing a SubsetSum instance that has the same
        answer (YES/NO) as the original Partition instance.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    Partition.validate(instance)

    numbers: List[int] = instance["numbers"]
    total = sum(numbers)

    if total % 2 == 1:
        # Odd total → Partition is NO.  Use a negative target to guarantee a
        # NO answer for SubsetSum.
        target = -1
    else:
        target = total // 2

    reduced = {"numbers": numbers, "target": target}
    # Validate the produced target instance as a sanity check.
    SubsetSum.validate(reduced)
    return reduced

