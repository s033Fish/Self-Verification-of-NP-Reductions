"""Reduction from Subset Sum to Partition.

The source problem (SubsetSum) expects an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

The target problem (Partition) expects an instance of the form::

    {"numbers": [b1, b2, ...]}

We construct a polynomial‑time transformation such that the Partition
instance is a *yes* instance iff the original Subset Sum instance is a
*yes* instance.

Reduction idea
==============
Let ``A`` be the multiset of numbers and ``S = sum(A)``.  For a target ``t``
with ``0 <= t <= S`` we add a single extra number ``x = S - 2*t`` to the
multiset.  The new total sum becomes ``S + x = 2·(S - t)`` which is even, and
any valid partition must place ``x`` in one of the two groups.  If the group
containing ``x`` also contains a subset of the original numbers that sums to
``t``, both groups will have size ``S - t``.  Consequently a partition exists
iff a subset of ``A`` sums to ``t``.

To handle targets larger than ``S/2`` we use the complement property of
Subset Sum: a subset sums to ``t`` iff the complementary subset sums to
``S - t``.  Therefore we replace ``t`` with ``S - t`` when ``t > S/2``.  For
invalid targets (negative or larger than ``S``) we return a trivially
unsatisfiable Partition instance – a single element with value ``1`` (odd
total, always a *no*).

The construction runs in linear time with respect to the size of the input
and uses only integer arithmetic, satisfying the polynomial‑time requirement.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, List[int]]:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"numbers"`` (list of non‑negative ints) and
        ``"target"`` (int).

    Returns
    -------
    dict
        A dictionary suitable for the Partition problem, i.e. ``{"numbers":
        [...]}``.
    """

    numbers: List[int] = instance.get("numbers", [])
    target: int = instance.get("target", 0)

    # Compute total sum of the original numbers.
    total = sum(numbers)

    # Cases where Subset Sum is definitively a NO.
    if target < 0 or target > total:
        # An odd total guarantees a NO for Partition.
        return {"numbers": [1]}

    # Use the complement if target is larger than half of the sum.
    if target > total / 2:
        target = total - target

    # Now 0 <= target <= total/2, so x = total - 2*target is non‑negative.
    x = total - 2 * target

    # Construct the Partition instance.
    return {"numbers": numbers + [x]}

