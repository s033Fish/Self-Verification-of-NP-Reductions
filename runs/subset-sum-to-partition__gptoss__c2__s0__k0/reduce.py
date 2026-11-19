"""Reduction from Subset Sum to Partition.

The source problem (SubsetSum) expects an instance of the form
    {"numbers": [a1, a2, ...], "target": t}
where all ``a_i`` are non‑negative integers and ``t`` is an integer.
The target problem (Partition) expects an instance of the form
    {"numbers": [b1, b2, ...]}
with non‑negative integers.

We construct a polynomial‑time reduction that maps any Subset‑Sum instance
to a Partition instance such that the Partition instance is a *yes*‑instance
iff the original Subset‑Sum instance is a *yes*‑instance.

Standard reduction:
    Let S = sum(numbers).  If we add an extra element ``e = S - 2*t`` to the
    list, the total sum becomes ``2*(S - t)`` and a partition of the new list
    into two equal halves of size ``S - t`` exists exactly when a subset of
    the original numbers sums to ``t``.

The element ``e`` must be non‑negative.  When ``t > S/2`` the value
``e`` becomes negative.  In that case we add ``d = 2*t - S`` (the absolute
value of ``e``) instead.  The total sum of the new list is then ``2*t`` and
each side of a valid partition must sum to ``t``.  Placing the added element
``d`` on one side forces the remaining numbers on that side to sum to
``t - d = S - t`` – i.e. a subset of the original numbers summing to the
complement of ``t``.  Since a subset sums to ``t`` iff a (different) subset
sums to ``S - t`` (take the complement of the subset), the reduction remains
correct.

Edge‑case handling follows the specifications of the source problem:
    * ``t < 0`` – always a *no* instance.  We return a simple Partition
      instance with an odd total (e.g. ``[1]``) which is a *no*.
    * ``t == 0`` – always a *yes* instance (empty subset).  The empty list is
      a valid *yes* Partition instance.
    * ``t > S`` – impossible to achieve, so we again return a known *no*
      Partition instance.

The function runs in linear time with respect to the size of the input list
and uses only integer arithmetic, satisfying the polynomial‑time requirement.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, List[int]]:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance: dict
        ``{"numbers": [...], "target": t}``

    Returns
    -------
    dict
        ``{"numbers": [...]}`` suitable for the Partition problem.
    """
    numbers: List[int] = instance.get("numbers", [])
    t: int = instance.get("target", 0)

    # Edge cases dictated by the Subset‑Sum definition.
    if t < 0:
        # Always a NO – return a Partition instance with odd total.
        return {"numbers": [1]}
    if t == 0:
        # Always YES – the empty list is a YES for Partition.
        return {"numbers": []}

    total = sum(numbers)
    if t > total:
        # Impossible to reach – return a known NO instance.
        return {"numbers": [1]}

    # Compute e = total - 2*t.  It may be negative.
    e = total - 2 * t
    if e >= 0:
        # Adding e (non‑negative) yields the classic reduction.
        new_numbers = numbers + [e]
    else:
        # e is negative; add its absolute value instead.
        d = -e  # = 2*t - total, guaranteed positive here.
        new_numbers = numbers + [d]

    return {"numbers": new_numbers}

