"""Reduction from Partition to Subset Sum.

The *source* problem is ``Partition`` defined in ``problems.py`` with an
instance format ``{"numbers": [a1, a2, ...]}``.  The *target* problem is
``SubsetSum`` with an instance format ``{"numbers": [a1, a2, ...], "target": t}``.

For a given list of non‑negative integers ``numbers`` we construct a
``SubsetSum`` instance that is a *yes* instance iff the original list can be
partitioned into two subsets of equal sum.

The classic reduction works as follows:

* Let ``total = sum(numbers)``.
* If ``total`` is even, set ``target = total // 2``.  A subset that sums to
  ``total // 2`` corresponds exactly to one side of a valid partition.
* If ``total`` is odd, a partition is impossible.  To preserve the equivalence
  we output a ``SubsetSum`` instance that is always a *no* instance.  The
  simplest choice is ``target = total + 1`` because no sub‑list can exceed the
  sum of all numbers.

Both cases run in linear time with respect to the length of ``numbers`` and
use only integer arithmetic, satisfying the polynomial‑time requirement.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with the key ``"numbers"`` mapping to a list of
        non‑negative integers.

    Returns
    -------
    dict
        A dictionary suitable for the SubsetSum problem containing the same
        ``numbers`` list and an appropriate ``target`` value.
    """

    numbers: List[int] = instance.get("numbers", [])
    total = sum(numbers)

    if total % 2 == 0:
        target = total // 2
    else:
        # No valid partition exists; choose a target larger than any possible sum.
        target = total + 1

    return {"numbers": numbers, "target": target}

