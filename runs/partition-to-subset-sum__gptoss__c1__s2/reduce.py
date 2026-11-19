"""Reduction from Partition to Subset Sum.

The source problem *Partition* asks whether a multiset of non‑negative
integers can be split into two groups with equal sum.  The target problem
*SubsetSum* asks whether some sub‑multiset sums to a given target value.

Given an instance of Partition, we construct an equivalent Subset Sum
instance as follows:

* Let ``S`` be the list of numbers and ``total`` its sum.
* If ``total`` is even, we set ``target = total // 2``.  A subset of ``S``
  summing to ``target`` corresponds exactly to a partition of ``S`` into two
  equal‑sum groups (the complement of the subset forms the other group).
* If ``total`` is odd, the Partition instance is a definite *no* instance.
  To preserve the answer we choose a target that is impossible for Subset
  Sum.  Any integer larger than ``total`` cannot be obtained because all
  numbers are non‑negative and the sum of any sub‑list is at most ``total``.
  We therefore use ``target = total + 1``.

The construction runs in linear time and uses only elementary arithmetic,
hence it is a polynomial‑time many‑one reduction.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers, matching the format defined in ``problems.py``
        for the Partition problem.

    Returns
    -------
    dict
        A dictionary with keys ``"numbers"`` (the same list) and ``"target"``
        (the integer described in the module docstring) suitable for the
        SubsetSum problem.
    """

    numbers: List[int] = instance.get("numbers", [])
    # Compute the total sum – Python's int handles arbitrarily large values.
    total = sum(numbers)

    if total % 2 == 0:
        # Even total: a yes‑instance of Partition corresponds to a yes‑instance
        # of SubsetSum with target half of the total.
        target = total // 2
    else:
        # Odd total: Partition is a no‑instance.  Choose a target larger than
        # any possible subset sum to guarantee a no‑instance for SubsetSum.
        target = total + 1

    return {"numbers": numbers, "target": target}

