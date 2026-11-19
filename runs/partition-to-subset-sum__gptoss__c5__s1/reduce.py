"""Reduction from Partition to Subset Sum.

The source problem is :class:`Partition` defined in ``problems.py``.
The target problem is :class:`SubsetSum` defined in the same file.

For a given Partition instance ``{"numbers": [...]}`` we construct a
Subset‑Sum instance ``{"numbers": [...], "target": t}`` such that the
answer to the Subset‑Sum instance is *yes* exactly when the answer to the
original Partition instance is *yes*.

Standard reduction:

* Let ``S`` be the total sum of the numbers.
* If ``S`` is odd, Partition is a definite *no*.  We therefore return a
  Subset‑Sum instance with a negative target (e.g. ``-1``) – the Subset‑Sum
  problem is defined to be *no* for any negative target.
* If ``S`` is even, we set the target to ``S // 2``.  A partition exists
  iff there is a subset of the numbers that sums to exactly half of the
  total, which is precisely the Subset‑Sum condition.

The reduction runs in linear time with respect to the size of the input
list and therefore satisfies the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import Partition, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A valid Partition instance – a dict with a ``"numbers"`` key.

    Returns
    -------
    dict
        A valid Subset‑Sum instance.
    """
    # Validate the source instance (will raise InvalidInstance on bad input).
    Partition.validate(instance)

    numbers: List[int] = instance["numbers"]
    total = sum(numbers)

    if total % 2 == 1:
        # Odd total → Partition answer is always No.  Use a negative target
        # because SubsetSum is defined to be No for any t < 0.
        target = -1
    else:
        target = total // 2

    reduced_instance = {"numbers": numbers.copy(), "target": target}
    # Validate the produced instance to guarantee correctness of the format.
    SubsetSum.validate(reduced_instance)
    return reduced_instance

