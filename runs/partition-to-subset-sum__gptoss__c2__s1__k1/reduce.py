"""Reduction from Partition to Subset Sum.

The source problem (Partition) asks whether the multiset of numbers can be
split into two groups with equal sum.  The target problem (SubsetSum) asks
whether some sub‑multiset sums to a given target.

The classic polynomial‑time reduction is straightforward:

* Let ``S`` be the total sum of the input numbers.
* If ``S`` is even, then a partition exists **iff** there is a subset that
  sums to ``S // 2``.  We therefore output the same list of numbers and set
  ``target`` to ``S // 2``.
* If ``S`` is odd, the Partition instance is a definite *no* instance.  Any
  Subset‑Sum instance that is a *no* instance will preserve correctness.  The
  simplest such instance is an empty list of numbers with a non‑zero target
  (e.g. ``target = 1``), because the empty sub‑list only achieves sum ``0``.

Both branches run in linear time with respect to the length of the input
list, which is polynomial.  The returned instance follows the format defined
in ``problems.py`` for the ``SubsetSum`` class.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to an equivalent Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers, as specified by the ``Partition`` problem.

    Returns
    -------
    dict
        A Subset‑Sum instance ``{"numbers": [...], "target": t}`` such that
        the Subset‑Sum answer is *yes* exactly when the original Partition
        answer is *yes*.
    """

    numbers: List[int] = list(instance.get("numbers", []))
    total = sum(numbers)

    # Even total: use the classic reduction.
    if total % 2 == 0:
        target = total // 2
        return {"numbers": numbers, "target": target}

    # Odd total: Partition is a guaranteed NO.  Return a Subset‑Sum NO.
    # An empty list with a non‑zero target is always unsatisfiable.
    return {"numbers": [], "target": 1}

