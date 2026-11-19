"""Reduction from Partition to Subset Sum.

The source problem *Partition* asks whether a multiset of non‑negative
integers can be split into two groups with equal sum.  The target problem
*SubsetSum* asks whether a sub‑multiset sums to a given target.

Given an instance of Partition we construct an equivalent SubsetSum
instance as follows:

* Let ``S`` be the total sum of the numbers.
* If ``S`` is even, we set the target to ``S // 2``.  A subset summing to
  ``S // 2`` exists exactly when the numbers can be partitioned into two
  equal‑sum groups.
* If ``S`` is odd, the Partition instance is a definite *no* (the total
  cannot be split equally).  We map this to a SubsetSum instance with a
  negative target (e.g. ``-1``).  By the problem definition a negative
  target is always a *no* instance, so the answers match.

The construction runs in linear time with respect to the length of the
input list and uses only integer arithmetic, satisfying the polynomial‑
time requirement.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a Subset Sum instance.

    Parameters
    ----------
    instance: dict
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers, as defined by the ``Partition`` class in
        ``problems.py``.

    Returns
    -------
    dict
        A dictionary with keys ``"numbers"`` and ``"target"`` representing
        an instance of the ``SubsetSum`` problem.  The returned instance is
        a *yes* instance if and only if the original Partition instance is
        a *yes* instance.
    """

    numbers: List[int] = instance.get("numbers", [])
    total = sum(numbers)

    if total % 2 == 0:
        target = total // 2
    else:
        # An odd total cannot be partitioned equally; map to a guaranteed
        # no-instance for Subset Sum by using a negative target.
        target = -1

    return {"numbers": numbers, "target": target}

