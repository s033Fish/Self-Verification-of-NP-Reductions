"""Reduction from Subset Sum to Partition.

The source problem is defined in :class:`problems.SubsetSum` and the target
problem in :class:`problems.Partition`.  Both classes only provide a
``validate`` classmethod that checks the instance format – they do **not**
provide solvers.  This file implements a polynomial‑time many‑one reduction
function ``reduce`` that maps a Subset‑Sum instance to a Partition instance
preserving the answer.

Reduction idea
==============
For a Subset‑Sum instance ``(N, t)`` with ``N`` a list of non‑negative integers
and ``t`` an integer, let ``S = sum(N)``.  If ``t`` is outside the range
``[0, S]`` the answer is trivially *no* (the numbers are non‑negative).  In this
case we return a Partition instance that is guaranteed to be a *no* instance –
any list with an odd total works, e.g. ``[1, 2]`` (total = 3).

If ``0 ≤ t ≤ S`` we use the classic reduction that adds a single extra number
``x = S - 2·t'`` where ``t' = min(t, S‑t)``.  The value ``t'`` is chosen so that
``x`` is never negative (when ``t > S/2`` we work with the complement target
``S‑t`` which is ≤ S/2).  The constructed list ``N' = N ∪ {x}`` has total sum
``2·(S - t')``; a partition of ``N'`` exists iff there is a subset of ``N``
+summing to ``t'`` – which is equivalent to the original Subset‑Sum question.

Both branches run in time linear in the size of the input, satisfying the
polynomial‑time requirement.
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
        ``"target"`` (int).  The instance is validated using
        :meth:`SubsetSum.validate`.

    Returns
    -------
    dict
        A valid Partition instance – a dictionary with a single key
        ``"numbers"`` – that is a *yes* instance iff the original Subset‑Sum
        instance is a *yes* instance.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the format is incorrect.
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])  # copy to avoid mutation
    target: int = instance["target"]
    total = sum(numbers)

    # Cases where the answer is known to be NO (target out of reachable range).
    if target < 0 or target > total:
        # Any Partition instance with an odd total sum is a definite NO.
        # The list [1, 2] has total 3 (odd) and consists of non‑negative ints.
        return {"numbers": [1, 2]}

    # Work with the smaller of target and its complement to guarantee a
    # non‑negative extra element.
    t_adj = target if target * 2 <= total else total - target
    extra = total - 2 * t_adj  # this is >= 0 by construction

    # Append the extra element and return the Partition instance.
    new_numbers = numbers + [extra]
    # Validate the target instance before returning (helps catch bugs).
    Partition.validate({"numbers": new_numbers})
    return {"numbers": new_numbers}

