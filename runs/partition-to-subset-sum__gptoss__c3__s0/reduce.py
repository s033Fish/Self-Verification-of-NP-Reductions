"""Reduction from Partition to Subset Sum.

The source problem (Partition) asks whether the multiset of numbers can be
split into two groups of equal sum.  This is equivalent to asking whether there
exists a subset whose sum is exactly half of the total sum (when the total is
even).  The target problem (SubsetSum) asks whether a given subset sums to a
specified target.

Given an instance ``{"numbers": [a1, a2, ...]}`` we construct a SubsetSum
instance as follows:

* Let ``total = sum(numbers)``.
* If ``total`` is even, the answer to Partition is *yes* exactly when the
  SubsetSum instance with the same numbers and ``target = total // 2`` is *yes*.
* If ``total`` is odd, Partition is always *no*.  We exploit the SubsetSum edge
  case that any instance with a negative target is automatically *no* (the
  definition states "t < 0 is always no").  Therefore we return a target of ``-1``
  (any negative integer works) while keeping the numbers unchanged.

Both transformations run in linear time in the size of the input, satisfying
the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict[str, List[int]]) -> Dict[str, object]:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers (the Partition format).

    Returns
    -------
    dict
        A dictionary with keys ``"numbers"`` and ``"target"`` representing a
        SubsetSum instance.  The returned instance satisfies the specification
        in ``problems.py`` and has the property that its answer is *yes* iff the
        original Partition instance's answer is *yes*.
    """

    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 == 0:
        # Even total – ask for a subset summing to half the total.
        target = total // 2
    else:
        # Odd total – Partition is impossible, use a negative target which is
        # always a "no" for SubsetSum.
        target = -1
    return {"numbers": numbers, "target": target}

