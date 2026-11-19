"""Reduction from Partition to Subset Sum.

The source problem (Partition) asks whether a multiset of non‑negative
integers can be split into two groups of equal sum.  The classic reduction
to Subset Sum is to ask whether there is a subset that sums to half of the
total.  If the total sum is odd the Partition instance is a definite *no*;
any Subset Sum instance that is also a *no* will do – we use a target that is
strictly larger than the sum of all numbers.

The function ``reduce`` below implements this transformation.  It runs in
polynomial time (linear in the number of numbers) and preserves the answer
exactly:

* If the total sum ``S`` is even, the returned Subset Sum instance has the
  same list of numbers and target ``S // 2``.  A partition exists iff a
  subset with that sum exists.
* If ``S`` is odd, the returned instance keeps the same numbers but uses a
  target of ``S + 1``.  No subset can reach a sum larger than the total, so
  the Subset Sum answer is ``False`` exactly when the Partition answer is
  ``False``.

Edge‑cases such as the empty list or the presence of zeros are handled
automatically by the above rules and match the specifications of both
problems.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict[str, List[int]]) -> Dict[str, object]:
    """Reduce a Partition instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers – exactly the format required by the
        ``Partition`` class in ``problems.py``.

    Returns
    -------
    dict
        A dictionary of the form ``{"numbers": [...], "target": t}`` suitable
        for the ``SubsetSum`` class.
    """
    numbers = list(instance["numbers"])
    total = sum(numbers)
    if total % 2 == 0:
        target = total // 2
    else:
        # Any target greater than the total sum guarantees a "no" answer.
        target = total + 1
    return {"numbers": numbers, "target": target}

