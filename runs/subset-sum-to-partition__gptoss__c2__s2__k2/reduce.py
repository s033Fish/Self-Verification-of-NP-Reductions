"""Reduction from Subset Sum to Partition.

The source problem (SUBSET SUM) instance format is a dictionary:
    {"numbers": [a1, a2, ...], "target": t}
where ``numbers`` is a list of non‑negative integers and ``target`` is an
integer (possibly negative).  The decision question is whether some sub‑list
of ``numbers`` sums exactly to ``target``.

The target problem (PARTITION) instance format is a dictionary:
    {"numbers": [b1, b2, ...]}
where the numbers are non‑negative integers.  The question is whether the
multiset can be split into two groups of equal sum.

We implement a polynomial‑time many‑one reduction.  The construction follows
the classic textbook reduction and handles all edge‑cases explicitly.

Reduction strategy
-------------------
Let ``A`` be the list of numbers from the Subset‑Sum instance and let ``S`` be
its sum.  Let ``t`` be the target (``t >= 0`` after the trivial cases).

* If ``t < 0`` the Subset‑Sum answer is always *no*.  We return a Partition
  instance with an odd total (e.g. ``[1]``) which is always a *no* instance.
* If ``t == 0`` the Subset‑Sum answer is always *yes* (empty sub‑list).  The
  empty list is a trivial *yes* Partition instance.
* For ``t > 0`` we add a single extra element ``extra`` to the list ``A``.
  The value of ``extra`` depends on the relation between ``S`` and ``2*t``:

  - If ``S < 2*t`` we set ``extra = 2*t - S``.  The new total becomes
    ``S + extra = 2*t`` and the required half‑sum is ``t``.  Because
    ``extra >= t`` (unless ``S == t`` where the original instance is already a
    *yes*), any subset achieving the half‑sum cannot use ``extra`` unless the
    original instance is already a *yes*.  Consequently the Partition instance
    is a *yes* exactly when the original Subset‑Sum instance is a *yes*.

  - Otherwise ``S >= 2*t`` and we set ``extra = S - 2*t`` (non‑negative).
    The new total is ``S + extra = 2*(S - t)`` and the required half‑sum is
    ``S - t``.  A subset achieving this half‑sum must either contain ``extra``
    (leaving a needed sum of ``t`` from the original numbers) or omit it
    (leaving a needed sum of ``S - t`` from the original numbers).  The two
    possibilities are complementary, so a feasible partition exists iff a
    subset of the original numbers sums to ``t``.

Both constructions use only non‑negative integers and run in linear time.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
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
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Edge cases handled directly.
    if target < 0:
        # Subset‑Sum is always NO; return a Partition instance with odd total.
        return {"numbers": [1]}
    if target == 0:
        # Always YES; the empty list is a trivial YES for Partition.
        return {"numbers": []}

    # General case: target > 0.
    total_sum = sum(numbers)
    if total_sum < 2 * target:
        extra = 2 * target - total_sum
        # The new total will be 2*target, half‑sum = target.
        new_numbers = numbers + [extra]
    else:
        extra = total_sum - 2 * target  # non‑negative
        # New total = 2*(total_sum - target), half‑sum = total_sum - target.
        new_numbers = numbers + [extra]

    return {"numbers": new_numbers}

