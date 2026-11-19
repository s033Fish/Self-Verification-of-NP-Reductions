"""Reduction from Partition to Subset Sum.

The source problem *Partition* asks whether a multiset of non‑negative
integers can be split into two groups with equal sum.  The target problem
*SubsetSum* asks whether some sub‑multiset sums to a given target integer.

The classic polynomial‑time reduction works as follows:

* Let ``S`` be the total sum of the numbers.
* If ``S`` is odd then the Partition instance is a definite **NO**.  For
  SubsetSum we can produce an instance that is also a definite **NO** by
  using a negative target (the definition guarantees ``t < 0`` is always
  unsatisfiable).  The actual list of numbers is irrelevant – an empty list
  suffices.
* If ``S`` is even we set the SubsetSum target to ``S // 2`` and keep the
  original list of numbers.  A subset that sums to ``S/2`` corresponds exactly
  to one side of a valid partition, and vice‑versa.

Both branches run in time linear in the size of the input, which is
polynomial.  The function ``reduce`` conforms to the interface expected by
the evaluation harness: it accepts a Partition instance (a ``dict`` with a
``"numbers"`` key) and returns a SubsetSum instance (a ``dict`` with
``"numbers"`` and ``"target"`` keys).
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to an equivalent SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers.

    Returns
    -------
    dict
        A SubsetSum instance.  If the total sum of the numbers is odd the
        returned instance is guaranteed to be a ``NO`` instance (negative
        target).  Otherwise the target is half the total sum.
    """

    numbers: List[int] = instance.get("numbers", [])
    total = sum(numbers)

    # Odd total -> Partition is impossible.  Produce a SubsetSum instance
    # that is also impossible by using a negative target.
    if total % 2 == 1:
        return {"numbers": [], "target": -1}

    # Even total -> use the same numbers and target = total // 2.
    return {"numbers": numbers.copy(), "target": total // 2}

