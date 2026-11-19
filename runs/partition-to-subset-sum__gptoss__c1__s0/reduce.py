"""Reduction from Partition to Subset Sum.

The source problem (Partition) asks whether a multiset of non‑negative
integers can be split into two groups with equal sum.  The target problem
SubsetSum asks whether a sub‑multiset sums to a given target.

The classic polynomial‑time reduction is:

* Let ``S`` be the total sum of the numbers.
* If ``S`` is even, ask the SubsetSum instance whether there is a subset
  summing to ``S // 2`` – such a subset exists exactly when the original
  instance can be partitioned.
* If ``S`` is odd, the Partition instance is a definite ``NO``.  To preserve
  this answer we produce a SubsetSum instance whose answer is also ``NO``.
  Because all numbers are non‑negative, any target larger than ``S`` is
  unattainable.  We therefore use ``S + 1`` as the target.

Both cases run in time linear in the size of the input, satisfying the
polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers, as defined by the ``Partition`` problem.

    Returns
    -------
    dict
        A dictionary with keys ``"numbers"`` and ``"target"`` forming a
        valid ``SubsetSum`` instance.  The returned instance is a *yes*
        instance iff the input instance is a *yes* instance.
    """

    numbers: List[int] = list(instance.get("numbers", []))
    total = sum(numbers)

    if total % 2 == 0:
        # Even total: ask for half the sum.
        target = total // 2
    else:
        # Odd total: impossible target ensures a NO answer.
        target = total + 1

    return {"numbers": numbers, "target": target}
