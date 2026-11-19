"""Reduction from Partition to Subset Sum.

The source problem is :class:`Partition` (defined in ``problems.py``).
The target problem is :class:`SubsetSum`.

For an instance ``{"numbers": [a1, a2, ...]}`` we construct the Subset Sum
instance ``{"numbers": [a1, a2, ...], "target": t}`` where ``t`` is the
desired half‑sum.

* If the total sum of the numbers is even, ``t`` is ``total // 2``.  In this
  case a partition exists iff there is a subset summing to ``t``.
* If the total sum is odd, a partition is impossible.  We therefore return a
  Subset‑Sum instance with a negative target (e.g. ``-1``) because the definition
  of SubsetSum guarantees a ``no`` answer for any negative target.

The reduction runs in linear time in the size of the input list.
"""

from __future__ import annotations

from typing import Dict, Any, List

from problems import Partition, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to the Partition input format.

    Returns
    -------
    dict
        A dictionary that conforms to the SubsetSum input format.  The answer
        to the returned instance is *yes* exactly when the answer to the
        original instance is *yes*.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.  The validation helpers live in ``problems.py``.
    Partition.validate(instance)

    numbers: List[int] = instance["numbers"]
    total = sum(numbers)

    if total % 2 != 0:
        # Odd total => Partition is always "no".  Use a negative target which
        # is guaranteed to be a "no" for SubsetSum according to its definition.
        target = -1
    else:
        target = total // 2

    # Build the target instance.  It must satisfy SubsetSum.validate; the
    # numbers list is already known to be non‑negative integers, and the target
    # we chose is an integer.
    reduced_instance: Dict[str, Any] = {"numbers": numbers, "target": target}
    SubsetSum.validate(reduced_instance)
    return reduced_instance
