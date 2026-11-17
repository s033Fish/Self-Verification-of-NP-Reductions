"""Reduction from Subset Sum to Partition.

The source problem is :class:`SubsetSum` (instance format `{"numbers": [...], "target": t}`).
The target problem is :class:`Partition` (instance format `{"numbers": [...]}`).

We implement a polynomial‑time many‑one reduction that preserves the answer.

Reduction strategy
-------------------
Given a Subset‑Sum instance ``N`` (list of non‑negative integers) and a target ``t``:

1. If ``t`` is negative or larger than the sum of ``N`` the answer is
   automatically **NO**.  We return a Partition instance that is known to be unsatisfiable – an odd total, e.g. `{"numbers": [1]}`.
2. Otherwise let ``S = sum(N)``.  Subset‑Sum asks whether some subset of ``N``
   sums to ``t``.  The complement of such a subset sums to ``S - t``; therefore
   the instance is a YES exactly when a subset sums to ``min(t, S - t)``.
   Define ``target = min(t, S - t)`` – this value is never larger than ``S/2``.
3. Construct an extra number ``x = S - 2 * target``.  By construction ``x`` is
   non‑negative because ``target ≤ S/2``.
4. Return the Partition instance whose numbers are the original list ``N``
   followed by the single extra number ``x``.

Correctness sketch
-------------------
*If a subset of ``N`` sums to ``target``*: put that subset together with the
extra element ``x`` in one partition side.  The side sum is ``target + x =
S - target``.  The remaining numbers sum to ``S - target`` as well, giving a
valid equal‑partition.

*Conversely*, any equal partition of the constructed list must have total sum
``2S`` (since ``S + x = 2S - 2*target``).  Each side therefore sums to ``S``.
Because ``x = S - 2*target`` is strictly less than ``S`` (unless ``target =
S/2``), exactly one side contains ``x``.  Removing ``x`` from that side leaves a
subset of the original numbers whose sum is ``target``.  Hence a partition
exists iff the original Subset‑Sum instance is a YES.

The reduction runs in linear time in the size of the input list, which is
polynomial.
"""

from __future__ import annotations

from typing import Dict, Any, List

# Import the problem classes for validation (optional but helpful).
from problems import SubsetSum, Partition


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"numbers"`` (list of non‑negative ints) and
        ``"target"`` (int).

    Returns
    -------
    dict
        A Partition instance dictionary ``{"numbers": [...]}``.
    """
    # Validate the source instance – will raise InvalidInstance if malformed.
    SubsetSum.validate(instance)

    numbers: List[int] = list(instance["numbers"])  # copy to avoid mutating input
    t: int = instance["target"]

    # Edge cases where the answer is definitely NO.
    if t < 0:
        # Any odd‑total partition instance is a guaranteed NO.
        return {"numbers": [1]}
    total = sum(numbers)
    if t > total:
        return {"numbers": [1]}

    # Choose the smaller of t and its complement.
    target = t if t <= total - t else total - t
    # Now target <= total/2, so x is non‑negative.
    x = total - 2 * target
    # Append the extra element.
    reduced_numbers = numbers + [x]
    reduced_instance = {"numbers": reduced_numbers}
    # Validate the produced instance (optional sanity check).
    Partition.validate(reduced_instance)
    return reduced_instance

