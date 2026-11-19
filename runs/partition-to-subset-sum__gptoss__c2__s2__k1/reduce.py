"""Reduction from Partition to Subset Sum.

The source problem (Partition) asks whether a multiset of non‑negative
integers can be split into two groups with equal sum.  The target problem
(`SubsetSum`) asks whether a sub‑multiset sums to a given target value.

The classic reduction is straightforward: a partition exists iff there is
some subset whose sum equals half of the total sum.  Therefore we map a
Partition instance ``{"numbers": a}`` to a SubsetSum instance
``{"numbers": a, "target": S//2}`` when the total sum ``S`` is even.  When
``S`` is odd the Partition instance is a definite *no*; to preserve the
answer we output a Subset Sum instance that is always *no* – an empty list of
numbers with a positive target (e.g. ``1``).

Both problems allow non‑negative integers of arbitrary size, and the
reduction runs in linear time with respect to the length of the input list,
which is polynomial.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to an equivalent Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers (the Partition instance).

    Returns
    -------
    dict
        A dictionary representing a Subset Sum instance with keys
        ``"numbers"`` (list of integers) and ``"target"`` (integer).

    The returned instance is a *yes* instance of Subset Sum exactly when the
    input is a *yes* instance of Partition.
    """

    numbers: List[int] = instance.get("numbers", [])
    total = sum(numbers)

    # If total sum is odd, Partition is impossible.  Return a Subset Sum
    # instance that is guaranteed to be a *no*.
    if total % 2 == 1:
        # An empty list cannot achieve a positive target.
        return {"numbers": [], "target": 1}

    # Even total – a partition exists iff there is a subset summing to half.
    target = total // 2
    return {"numbers": numbers.copy(), "target": target}

