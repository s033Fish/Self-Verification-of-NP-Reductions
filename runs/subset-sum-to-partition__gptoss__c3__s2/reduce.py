"""Reduction from Subset Sum to Partition.

Given a Subset‑Sum instance with numbers a_i (non‑negative) and target t,
let B = sum(a_i).  If t is outside [0, B] the answer is always *no*; we return
a trivially unsatisfiable Partition instance.
Otherwise we may assume t ≤ B/2 by replacing t with B‑t (a subset sums to t
iff its complement sums to B‑t).  Define
    extra = B - 2*t   (non‑negative).
Create the Partition instance consisting of the original numbers together with
the single extra element.
The total sum is B + extra = 2*(B - t), which is even.  A partition must split
the numbers into two groups of sum B - t.  Such a partition exists exactly when
there is a subset of the original numbers summing to t (or equivalently B‑t),
because the extra element must be placed on the side that does **not** contain
that subset.  Hence the reduction is correct and runs in linear time.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SubsetSum, Partition


def reduce(instance: Dict) -> Dict:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance:
        Dictionary with keys "numbers" (list of non‑negative ints) and
        "target" (int).

    Returns
    -------
    dict
        A Partition instance preserving the yes‑answer.
    """
    # Validate the source instance.
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])
    target: int = int(instance["target"])
    total = sum(numbers)

    # Cases where Subset‑Sum is definitely a no‑instance.
    if target < 0 or target > total:
        return {"numbers": [1]}  # odd total → never partitionable

    # Ensure we work with the smaller of t and total - t.
    t = target if target <= total - target else total - target
    extra = total - 2 * t  # guaranteed non‑negative

    reduced_numbers = numbers + [extra]
    # Validate the produced Partition instance.
    Partition.validate({"numbers": reduced_numbers})
    return {"numbers": reduced_numbers}

