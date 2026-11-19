"""Reduction from Subset Sum to Partition.

The source problem (Subset Sum) is defined by an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

where ``numbers`` are non‑negative integers (duplicates allowed) and ``t`` is
an integer (may be negative).  The answer is *yes* iff a sub‑multiset of
``numbers`` sums exactly to ``t``.

The target problem (Partition) expects an instance of the form::

    {"numbers": [b1, b2, ...]}

and is *yes* iff the multiset can be split into two groups with equal sum.

We implement the classic polynomial‑time reduction:

* Let ``S`` be the sum of the input numbers.
* Compute ``extra = abs(S - 2 * t)`` – this value is always a non‑negative
  integer.
* Return the Partition instance consisting of the original numbers plus the
  extra element.

Correctness sketch
-------------------
Let ``extra = S - 2*t`` when ``S >= 2*t`` (the other case is symmetric).  The
total sum of the new list is ``S + extra = 2(S - t)``; each side of a valid
partition must therefore sum to ``S - t``.

*If the Subset‑Sum instance is a *yes* instance*: there exists a subset ``X``
with sum ``t``.  Its complement ``C`` sums to ``S - t`` and can be placed on
one side of the partition.  The other side consists of ``X`` together with the
extra element ``extra`` whose sum is ``t + (S - 2*t) = S - t``.  Hence a
partition exists.

*If the Partition instance is a *yes* instance*: consider the side that
contains the extra element.  Removing ``extra`` leaves a subset of the
original numbers whose sum is ``(S - t) - extra = t`` (when ``extra = S - 2*t``)
or ``S - t`` (when ``extra = 2*t - S``).  In either case we obtain a subset of
the original numbers that sums to ``t`` (or its complement, which also yields a
subset summing to ``t``).  Thus the original Subset‑Sum instance is a *yes*
instance.

Edge cases
~~~~~~~~~~
* ``t < 0`` – Subset‑Sum is always *no*.  We return a Partition instance with an
  odd total (e.g., ``[1]``), which is always *no*.
* ``t == 0`` – the reduction works unchanged; ``extra = S`` and the instance is
  trivially partitionable.
* Empty ``numbers`` – handled correctly by the formula; when ``t == 0`` the
  returned instance is ``[0]`` (a *yes* instance), otherwise we fall back to the
  odd‑total construction.

The function runs in linear time with respect to the length of the input list,
which is polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, List[int]]:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"numbers"`` (list of non‑negative ints) and
        ``"target"`` (int).

    Returns
    -------
    dict
        A Partition instance ``{"numbers": [...]}`` preserving the answer.
    """

    numbers: List[int] = instance.get("numbers", [])
    target: int = instance.get("target", 0)

    # If the target is negative, Subset‑Sum is always a NO instance.
    # Produce a Partition instance with an odd total sum, which is always NO.
    if target < 0:
        return {"numbers": [1]}  # odd sum => no partition

    total = sum(numbers)
    extra = abs(total - 2 * target)

    # The extra element may be zero; zeros do not affect the Partition answer.
    reduced_numbers = numbers + [extra]
    return {"numbers": reduced_numbers}

