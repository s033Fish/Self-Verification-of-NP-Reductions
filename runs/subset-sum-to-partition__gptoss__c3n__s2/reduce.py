"""Reduction from Subset Sum to Partition.

The source problem (Subset Sum) instance format is:
    {"numbers": [a1, a2, ...], "target": t}
The target problem (Partition) instance format is:
    {"numbers": [b1, b2, ...]}

Both problems are defined in ``problems.py`` with a ``validate`` class
method.  This module provides a single function ``reduce`` that maps a
Subset‑Sum instance to a Partition instance preserving the answer.

The classic reduction works as follows.  Let ``S`` be the sum of the
original numbers and let ``t`` be the target.  If ``t`` is negative the
Subset‑Sum answer is always *no*; we therefore return a Partition instance
that is trivially *no* (an odd total).  If ``t`` is zero the answer is
always *yes*; we return the empty list which is a yes‑instance for
Partition.

For non‑negative ``t`` we choose a target ``t'`` that satisfies ``2*t' >=
S``.  If the original ``t`` already satisfies this inequality we keep it;
otherwise we replace ``t`` by its complement ``S - t`` – note that the
original instance is a yes‑instance iff a subset summing to ``S - t``
exists (the complement of a subset summing to ``t``).  With such a ``t'``
the value ``y = 2*t' - S`` is guaranteed to be a non‑negative integer.
Adding ``y`` to the multiset of numbers yields a new total ``2*t'``; a
partition into two equal halves of size ``t'`` exists exactly when the
original Subset‑Sum instance is a yes‑instance.

The construction runs in linear time and uses only integer arithmetic,
hence it is polynomial‑time.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SubsetSum, Partition


def reduce(instance: Dict) -> Dict:
    """Reduce a Subset‑Sum instance to a Partition instance.

    The returned instance is a dictionary suitable for ``Partition``.
    ``reduce`` runs in O(n) time where *n* is the number of input
    numbers.
    """
    # Validate the source instance – this will raise if malformed.
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])
    t: int = instance["target"]
    total = sum(numbers)

    # Edge cases dictated by the problem statements.
    if t == 0:
        # Subset‑Sum is always yes; an empty list is a yes‑instance for
        # Partition (both groups empty).
        return {"numbers": []}
    if t < 0:
        # Subset‑Sum is always no; produce a Partition instance that is
        # certainly no – a single element creates an odd total.
        return {"numbers": [1]}

    # At this point t > 0.
    # Choose a target t' such that 2*t' >= total.
    if 2 * t >= total:
        t_prime = t
    else:
        # Use the complement; the original instance is yes iff there is a
        # subset summing to total - t.
        t_prime = total - t

    # y = 2*t' - total is guaranteed to be >= 0.
    y = 2 * t_prime - total
    # Append y to the list of numbers.
    new_numbers = numbers + [y]

    # Validate the target instance before returning (optional but helpful).
    Partition.validate({"numbers": new_numbers})
    return {"numbers": new_numbers}

