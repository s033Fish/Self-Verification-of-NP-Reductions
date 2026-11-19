"""Reduction from Partition to Subset Sum.

The source problem is :class:`Partition` defined in ``problems.py``.
The target problem is :class:`SubsetSum` defined in the same file.

For a given instance ``{"numbers": [a1, a2, ...]}`` we construct a
``SubsetSum`` instance ``{"numbers": [...], "target": t}`` such that the
answer to the Subset Sum instance is *yes* iff the original Partition
instance is *yes*.

Standard reduction: a partition exists iff there is a subset whose sum
equals half of the total sum.  If the total sum is odd, the answer is
always *no* for Partition, and we can map it to a Subset Sum instance
that is also always *no* – Subset Sum with a negative target is defined
to be a *no* instance.

The reduction runs in linear time in the size of the input list.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Partition, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to :class:`Partition`'s instance format.

    Returns
    -------
    dict
        A dictionary that conforms to :class:`SubsetSum`'s instance format.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong, matching the behaviour expected by the evaluation
    # harness.
    Partition.validate(instance)

    numbers: List[int] = instance["numbers"]
    total = sum(numbers)

    if total % 2 == 1:
        # Odd total → Partition is always NO.  Use a negative target, which
        # is guaranteed to be a NO instance for Subset Sum (see its docstring).
        target = -1
    else:
        target = total // 2

    reduced_instance = {"numbers": numbers.copy(), "target": target}

    # Validate the produced instance to catch accidental mistakes early.
    SubsetSum.validate(reduced_instance)
    return reduced_instance

