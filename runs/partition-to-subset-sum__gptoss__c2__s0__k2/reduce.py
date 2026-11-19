"""Reduction from Partition to Subset Sum.

The source problem (Partition) expects an instance of the form::

    {"numbers": [a1, a2, ...]}

where the ``a_i`` are non‑negative integers.  The answer is *yes* iff the
multiset can be split into two groups of equal sum.

The target problem (SubsetSum) expects an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

and is *yes* iff some sub‑multiset sums exactly to ``t``.

Standard textbook reduction:

* Let ``S`` be the total sum of the numbers.
* If ``S`` is even, a partition exists exactly when there is a subset that
  sums to ``S // 2``.  Hence we map the instance to the same list of numbers
  with target ``S // 2``.
* If ``S`` is odd, a partition is impossible.  To preserve the answer we need
  to produce a SubsetSum instance that is also always *no*.  The SubsetSum
  specification states that any negative target yields a *no* answer, regardless
  of the numbers.  Therefore we use a negative target (e.g. ``-1``).

Both branches run in linear time in the length of the input list, which is
polynomial.  Edge cases are handled automatically:

* Empty list → ``S = 0`` (even) → target ``0``.  SubsetSum with empty numbers
  and target ``0`` is a *yes* instance, matching Partition's answer.
* Lists containing zeros are unaffected because they do not change ``S``.

The function below follows the exact signature required by the task runner:
``reduce(instance) -> instance``.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Partition instance to an equivalent SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary with a single key ``"numbers"`` mapping to a list of
        non‑negative integers (the Partition instance).

    Returns
    -------
    dict
        A SubsetSum instance ``{"numbers": [...], "target": t}`` such that the
        SubsetSum answer is *yes* exactly when the original Partition answer is
        *yes*.
    """

    # Extract the list of numbers.  The caller (the benchmark harness) is
    # guaranteed to provide a valid Partition instance, so we do not perform
    # exhaustive validation here – the reduction must be fast and simple.
    numbers: List[int] = instance["numbers"]

    total = sum(numbers)

    if total % 2 == 0:
        # Even total: ask for a subset that sums to half of it.
        target = total // 2
    else:
        # Odd total: partition is impossible.  Use a negative target which is
        # guaranteed to be a "no" instance for SubsetSum.
        target = -1

    return {"numbers": numbers, "target": target}

