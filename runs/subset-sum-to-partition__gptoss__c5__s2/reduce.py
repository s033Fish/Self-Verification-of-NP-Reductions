"""Reduction from Subset Sum to Partition.

The source problem is defined in ``problems.SubsetSum`` and expects an
instance of the form ``{"numbers": [...], "target": t}``.  The target problem
is ``problems.Partition`` which expects ``{"numbers": [...]}``.

We implement a polynomial‑time many‑one reduction.  For a Subset Sum instance
with numbers ``a_1,…,a_n`` and target ``t`` let ``S = sum(a_i)``.

* If ``t < 0`` or ``t > S`` the Subset Sum instance is a definite **NO**.
  We return a Partition instance with an odd total (e.g. ``[1]``) which is
  always a **NO** instance.
* Otherwise ``0 ≤ t ≤ S``.  Define ``extra = |S - 2*t|`` (which is a
  non‑negative integer).  Return the numbers ``a_1,…,a_n, extra``.

Correctness sketch:
--------------------
Let ``P`` be the returned list and ``S' = sum(P) = S + extra = 2*max(t, S‑t)``.
The total ``S'`` is even, so a partition exists iff there is a subset of ``P``
that sums to ``S'/2 = max(t, S‑t)``.

* If a subset of the original numbers sums to ``t`` then, together with the
  element ``extra``, we obtain a subset of ``P`` that sums to ``t + extra``.
  Since ``extra = |S‑2*t|`` this sum equals ``max(t, S‑t)``.
* Conversely, any subset of ``P`` that reaches ``max(t, S‑t)`` either contains
  ``extra`` or not.  If it contains ``extra`` the remaining numbers sum to
  ``max(t, S‑t) - extra = min(t, S‑t)`` which is exactly ``t`` when ``t ≤ S/2``
  or ``S‑t`` when ``t > S/2``.  In the latter case a subset summing to ``S‑t``
  exists iff a subset summing to ``t`` exists (by taking the complement).
  If the subset does not contain ``extra`` it must sum directly to
  ``max(t, S‑t)`` which again corresponds to a subset of the original numbers
  summing to ``t`` (or ``S‑t``).  Hence a partition exists exactly when the
  Subset Sum instance is a YES instance.

The construction runs in linear time and uses only elementary arithmetic,
therefore it satisfies the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SubsetSum, Partition


def reduce(instance: Dict) -> Dict:
    """Reduce a Subset Sum instance to a Partition instance.

    Parameters
    ----------
    instance: dict
        Must satisfy ``SubsetSum.validate``.

    Returns
    -------
    dict
        An instance suitable for ``Partition.validate`` such that the answer
        to the Partition instance is *yes* iff the answer to the original
        Subset Sum instance is *yes*.
    """
    # Validate the source instance (will raise if malformed).
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])  # copy to avoid mutation
    target: int = instance["target"]

    total = sum(numbers)

    # Cases where Subset Sum is trivially NO.
    if target < 0 or target > total:
        # An odd total guarantees a NO answer for Partition.
        return {"numbers": [1]}

    # Compute the extra element.
    extra = abs(total - 2 * target)
    # Append the extra element (zero is allowed and does not affect the answer).
    reduced_numbers = numbers + [extra]

    # Validate the produced target instance before returning.
    Partition.validate({"numbers": reduced_numbers})
    return {"numbers": reduced_numbers}

