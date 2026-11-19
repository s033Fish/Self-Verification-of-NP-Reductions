"""Reduction from Partition to Subset Sum.

The source problem *Partition* asks whether a multiset of non‑negative
integers can be split into two groups with equal sum.  The target problem
*SubsetSum* asks whether some sub‑multiset sums to a given target integer.

Standard reduction:
    * Let ``S`` be the total sum of the numbers.
    * If ``S`` is odd, the Partition instance is a definite *no*.
      We therefore return a Subset‑Sum instance with a negative target
      (e.g. ``-1``).  By the definition of SubsetSum, any instance with a
      negative target is a *no* instance.
    * If ``S`` is even, the Partition instance is a *yes* exactly when a
      subset sums to ``S/2``.  Hence we return the same list of numbers and
      set ``target`` to ``S // 2``.

Both cases are computable in linear time, satisfying the polynomial‑time
requirement.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance: dict
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers, matching the format used by the provided
        ``Partition`` class.

    Returns
    -------
    dict
        A dictionary with keys ``"numbers"`` and ``"target"`` representing a
        valid SubsetSum instance.  The returned instance is a *yes* exactly
        when the input Partition instance is a *yes*.
    """

    numbers: List[int] = instance.get("numbers", [])
    total = sum(numbers)

    # If total is odd, Partition is always NO.  Use a negative target so that
    # SubsetSum is also always NO (t < 0 ⇒ NO by definition).
    if total % 2 == 1:
        return {"numbers": numbers, "target": -1}

    # Even total: Partition YES iff there exists a subset with sum total/2.
    target = total // 2
    return {"numbers": numbers, "target": target}

