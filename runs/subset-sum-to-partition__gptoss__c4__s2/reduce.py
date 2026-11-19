"""Reduction from Subset Sum to Partition.

The source problem is :class:`SubsetSum` (see ``problems.py``) and the target
problem is :class:`Partition`.  Both problems operate on lists of non‑negative
integers.  The reduction must run in polynomial time and preserve the answer.

Standard reduction (with parity trick):

Given numbers ``a_1,…,a_n`` and target ``t`` (with ``0 ≤ t ≤ sum(a)``) we
construct the list

    B = [2·a_1, 2·a_2, …, 2·a_n, 2·t+1, 2·(sum(a)‑t)+1]

All numbers coming from the original set are even, the two added numbers are odd.
The total sum of ``B`` is ``4·sum(a)+2`` which is even, and the required half‑sum is
``2·sum(a)+1`` (odd).  Because the sum of any subset of the even numbers is even,
any subset that reaches the odd half‑sum must contain exactly one of the two odd
numbers.  Consequently a partition exists iff there is a subset of the even
numbers whose sum equals ``2·(sum(a)‑t)`` – i.e. a subset of the original numbers
summing to ``sum(a)‑t``.  By taking complements this is equivalent to the
original Subset‑Sum instance having a subset that sums to ``t``.

Edge cases where Subset‑Sum is a guaranteed *no* instance (``t < 0`` or ``t >
sum(a)``) are reduced to a trivially unsatisfiable Partition instance – a single
odd number – which is always a *no* instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SubsetSum, Partition


def _trivial_no_instance() -> Dict[str, List[int]]:
    """Return a Partition instance that is always a *no* instance.

    The list ``[1]`` has an odd total sum, making partition impossible.
    """

    instance = {"numbers": [1]}
    Partition.validate(instance)
    return instance


def reduce(instance: Dict) -> Dict:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance:
        A dictionary matching the format of :class:`SubsetSum` – it must contain
        ``"numbers"`` (list of non‑negative ints) and ``"target"`` (int).

    Returns
    -------
    dict
        A valid Partition instance whose answer matches the source instance.
    """

    # Validate source instance.
    SubsetSum.validate(instance)

    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Immediate NO cases.
    if target < 0:
        return _trivial_no_instance()

    total = sum(numbers)
    if target > total:
        return _trivial_no_instance()

    # All‑zero case – the only YES target is 0.
    if total == 0:
        if target == 0:
            result = {"numbers": []}
            Partition.validate(result)
            return result
        else:
            return _trivial_no_instance()

    # Standard reduction with parity trick.
    doubled = [2 * a for a in numbers]               # even numbers
    odd1 = 2 * target + 1                           # odd
    odd2 = 2 * (total - target) + 1                 # odd
    new_numbers = doubled + [odd1, odd2]

    result = {"numbers": new_numbers}
    Partition.validate(result)
    return result

