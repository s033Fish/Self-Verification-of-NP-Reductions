"""Reduction from Partition to Subset Sum.

The source problem *Partition* asks whether a multiset of non‑negative
integers can be split into two groups with equal total sum.  The target
problem *SubsetSum* asks whether some sub‑multiset sums to a given target
value.

Given an instance of Partition represented as {"numbers": [a1, a2, ...]}
we construct a SubsetSum instance {"numbers": same_list, "target": t}
such that the SubsetSum instance is a *yes* exactly when the original
Partition instance is a *yes*.

The classic reduction uses the fact that a partition exists iff there is
some subset whose sum is half of the total sum.  Let S be the sum of all
numbers.

* If S is even, we set t = S // 2.  Then a subset of sum t corresponds to one side of a valid partition.
* If S is odd, a partition is impossible.  We must therefore produce a
  SubsetSum instance that is also impossible.  Because all numbers are non‑negative, any subset sum is at most S.  Choosing t = S + 1 guarantees that no subset can reach the target, yielding a *no*.

Both cases run in linear time with respect to the size of the input list,
which is polynomial.  Edge cases (empty list, zeros, etc.) are handled
correctly by the same logic.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to an equivalent SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key "numbers" mapping to a list of
        non‑negative integers, as defined by the ``Partition`` problem.

    Returns
    -------
    dict
        A dictionary suitable for the ``SubsetSum`` problem, containing the
        same "numbers" list and a computed "target" value.
    """
    numbers: List[int] = instance.get("numbers", [])
    total = sum(numbers)

    if total % 2 == 0:
        target = total // 2
    else:
        # Any target larger than the total sum is unattainable because all
        # numbers are non‑negative.
        target = total + 1

    return {"numbers": numbers, "target": target}


__all__ = ["reduce"]
