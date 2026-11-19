"""Reduction from Partition to Subset Sum.

The source problem is :class:`Partition` defined in ``problems.py``.
The target problem is :class:`SubsetSum` defined in the same file.

For an instance ``{"numbers": [a1, a2, ...]}`` we compute the total sum ``S``.
* If ``S`` is odd, the Partition instance is a definite *no* (by the
  problem statement).  We therefore return a Subset‑Sum instance that is
  also a definite *no*.  The simplest way is to use an empty list of
  numbers and a negative target – the Subset‑Sum definition guarantees a
  *no* answer for any negative target.
* If ``S`` is even, we set ``target = S // 2`` and keep the same list of
  numbers.  A subset that sums to ``target`` corresponds exactly to one of
  the two partitions of equal sum, so the answers coincide.

Both branches run in linear time in the size of the input, satisfying the
polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Partition, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce a Partition instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the Partition format, i.e. ``{"numbers": …}``.

    Returns
    -------
    dict
        A dictionary adhering to the SubsetSum format.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if
    # the input is malformed, matching the behaviour expected by the task.
    Partition.validate(instance)

    numbers: List[int] = instance["numbers"]
    total = sum(numbers)

    if total % 2 == 1:
        # Odd total → Partition is a definite NO.  Produce a Subset‑Sum
        # instance that is also a definite NO.  An empty list with a
        # negative target works because the definition states that any
        # t < 0 is always a NO.
        return {"numbers": [], "target": -1}
    else:
        target = total // 2
        return {"numbers": numbers.copy(), "target": target}
