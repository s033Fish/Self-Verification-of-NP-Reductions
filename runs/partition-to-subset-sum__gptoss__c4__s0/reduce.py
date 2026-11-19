"""Reduction from Partition to Subset Sum.

The source problem is :class:`Partition` defined in ``problems.py``.  An
instance is a dictionary ``{"numbers": [a1, a2, ...]}`` where the numbers are
non‑negative integers.  The answer is *yes* iff the multiset can be split into
two groups with equal sum.

The target problem is :class:`SubsetSum`.  An instance is a dictionary
``{"numbers": [...], "target": t}``.  The answer is *yes* iff some sub‑list of
``numbers`` sums exactly to ``t``.

The classic polynomial‑time many‑one reduction is:

* Let ``S = sum(numbers)``.
* If ``S`` is even, ask the Subset‑Sum instance ``target = S // 2`` – a subset
  of sum ``S/2`` exists exactly when the original multiset can be partitioned.
* If ``S`` is odd, the Partition instance is a definite *no*.  We map it to a
  Subset‑Sum instance with a negative target (e.g. ``-1``).  By the definition
  of Subset‑Sum, any instance with ``target < 0`` is a *no* instance, regardless
  of the numbers.

Both branches run in linear time and produce a valid Subset‑Sum instance.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key ``"numbers"`` containing a list of
        non‑negative integers.  The caller is expected to have validated the
        instance using ``Partition.validate``; this function does not perform
        validation itself to keep the runtime linear.

    Returns
    -------
    dict
        A Subset‑Sum instance ``{"numbers": [...], "target": t}`` such that the
        answer to the Subset‑Sum instance is *yes* exactly when the answer to
        the original Partition instance is *yes*.
    """

    numbers: List[int] = instance["numbers"]  # type: ignore[index]
    total = sum(numbers)
    if total % 2 == 0:
        # Even total – ask for a subset of half the sum.
        target = total // 2
    else:
        # Odd total – the Partition instance is a definite NO.  Use a negative
        # target which is always a NO for Subset‑Sum.
        target = -1
    return {"numbers": numbers, "target": target}

