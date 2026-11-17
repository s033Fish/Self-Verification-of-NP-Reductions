"""Reduction from Subset Sum to Partition.

The source problem is :class:`SubsetSum` (see ``problems.py``) and the target
problem is :class:`Partition`.  Both problems are defined in the same module
``problems.py`` and expose the class methods ``validate`` and ``is_yes``.

The reduction implements the classic polynomial‑time transformation:

* Let ``numbers`` be the list of non‑negative integers and ``t`` the target.
* Let ``S = sum(numbers)``.
* If ``t`` is negative, larger than ``S`` or ``t`` is not reachable, the
  Subset‑Sum instance is a definite **NO**.  We map such instances to a known
  non‑partitionable list (e.g. ``[1]`` whose total sum is odd).
* If ``t == 0`` the Subset‑Sum instance is always **YES**; we map it to the
  empty list which is trivially partitionable.
* Otherwise we may assume ``0 < t <= S``.  Subset‑Sum is symmetric with respect
  to complements: a subset summing to ``t`` exists iff a subset summing to
  ``S - t`` exists.  Therefore we replace ``t`` by ``min(t, S - t)`` so that
  ``t <= S/2``.
* Define ``extra = S - 2*t`` (which is non‑negative after the previous step).
  Append ``extra`` to the original list.  The new total sum is
  ``S + extra = 2 * (S - t)`` and a partition of this list into two equal
  halves of sum ``S - t`` exists exactly when a subset of the original numbers
  sums to ``t``.

The transformation runs in linear time and uses only integer arithmetic,
hence it satisfies the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SubsetSum, Partition


def reduce(instance: Dict) -> Dict:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"numbers"`` (list of non‑negative ints) and
        ``"target"`` (int).  It is assumed to be a valid Subset‑Sum instance –
        the caller may have validated it already.

    Returns
    -------
    dict
        A Partition instance (a dict with a single key ``"numbers"``).
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong, matching the behaviour of other reductions.
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])
    target: int = int(instance["target"])  # ensure plain int

    # Edge cases that are trivially NO for Subset‑Sum.
    if target < 0:
        # Any Partition instance with an odd total sum is a guaranteed NO.
        return {"numbers": [1]}
    total = sum(numbers)
    if target > total:
        return {"numbers": [1]}

    # Edge case: target == 0 is always YES.
    if target == 0:
        # Empty list is a YES instance for Partition.
        return {"numbers": []}

    # Use complement symmetry to ensure target <= total // 2.
    if target > total - target:
        target = total - target

    # Now target <= total/2, so extra = total - 2*target is non‑negative.
    extra = total - 2 * target
    # Append the extra element (could be 0, which is harmless).
    new_numbers = numbers + [extra]
    # Validate the produced Partition instance before returning.
    Partition.validate({"numbers": new_numbers})
    return {"numbers": new_numbers}

