"""Reduction from Partition to Subset Sum.

The source problem is :class:`Partition` defined in ``problems.py``.
The target problem is :class:`SubsetSum` defined in the same file.

For an instance ``{"numbers": [a1, a2, ...]}`` we compute the total sum ``S``.
* If ``S`` is odd the Partition instance is a definite *no* instance.  We map
  it to a Subset‑Sum instance with a negative target (e.g. ``-1``) because the
  specification guarantees that any target ``t < 0`` yields a *no* answer.
* Otherwise ``S`` is even and the Partition instance is a *yes* iff there is a
  subset of the numbers that sums to ``S // 2``.  Therefore we set the target to
  ``S // 2`` and reuse the same list of numbers.

Both transformations run in linear time, which is polynomial in the size of
the input.
"""

from __future__ import annotations

from typing import Dict, Any

from problems import Partition, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to an equivalent Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to :class:`Partition`'s format.  It is
        assumed to have been validated already (the caller may call
        ``Partition.validate`` if desired).

    Returns
    -------
    dict
        A dictionary that conforms to :class:`SubsetSum`'s format and has the
        property that the answer to the Subset‑Sum instance is *yes* exactly
        when the answer to the original Partition instance is *yes*.
    """

    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # format is wrong, matching the behaviour of the other problem classes.
    Partition.validate(instance)

    numbers = list(instance["numbers"])  # make a shallow copy to avoid mutation
    total = sum(numbers)

    if total % 2 == 1:
        # Odd total → Partition is always NO.  Choose a negative target which
        # is guaranteed to be a NO for Subset‑Sum.
        target = -1
    else:
        target = total // 2

    reduced_instance = {"numbers": numbers, "target": target}

    # Validate the produced target instance for sanity.
    SubsetSum.validate(reduced_instance)
    return reduced_instance

