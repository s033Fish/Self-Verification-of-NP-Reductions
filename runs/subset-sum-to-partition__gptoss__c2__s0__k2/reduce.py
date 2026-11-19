"""Reduction from Subset Sum to Partition.

The source problem (SubsetSum) instance format::

    {"numbers": [a1, a2, ...], "target": t}

The target problem (Partition) instance format::

    {"numbers": [b1, b2, ...]}

We construct a polynomial‑time mapping such that the Partition instance is a
YES‑instance iff the original Subset‑Sum instance is a YES‑instance.

Reduction idea
--------------
Let ``S = sum(numbers)`` and let ``t`` be the target.  If ``t`` is outside the
range ``[0, S]`` the answer is trivially NO.  For ``0 ≤ t ≤ S`` we use the well‑
known trick of adding a single extra element ``K = S - 2*t'`` where ``t'`` is
chosen to be the smaller of ``t`` and ``S - t``.  ``t'`` satisfies ``t' ≤ S/2``
so ``K`` is non‑negative.  The new multiset is ``numbers ∪ {K}``.  Its total sum
is ``2*(S - t')`` and each side of a valid partition must sum to ``S - t'``.

If a subset of the original numbers sums to ``t'`` then placing that subset
along with ``K`` on one side yields exactly ``S - t'``; the remaining numbers
automatically sum to the same value, giving a valid partition.  Conversely, any
partition must place ``K`` on one side; the remaining numbers on that side must
sum to ``t'`` which yields a subset‑sum solution.  Because a subset sums to ``t``
iff it sums to ``S - t`` (by taking the complement), using ``t' = min(t, S-t)``
preserves the answer for all feasible ``t``.

Edge cases are handled explicitly:
* ``t < 0`` or ``t > S`` – always NO; we return a Partition instance with an odd
  total (e.g., ``[1]``) which is a guaranteed NO.
* ``t == 0`` – always YES; we return the empty list, which is a YES for Partition.
* Empty ``numbers`` list – covered by the above logic.

The function runs in linear time with respect to the size of the input list.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, List[int]]:
    """Reduce a Subset‑Sum instance to a Partition instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"numbers"`` (list of non‑negative ints) and
        ``"target"`` (int).

    Returns
    -------
    dict
        A Partition instance dictionary with key ``"numbers"``.
    """
    numbers: List[int] = instance.get("numbers", [])
    t: int = instance.get("target", 0)

    # Basic validation – the problem definitions guarantee non‑negative numbers.
    S = sum(numbers)

    # Cases where the Subset‑Sum answer is definitively NO.
    if t < 0 or t > S:
        # An odd total guarantees a NO for Partition.
        return {"numbers": [1]}

    # The Subset‑Sum answer is always YES when t == 0 (empty sub‑list).
    if t == 0:
        # Empty list is a YES instance for Partition.
        return {"numbers": []}

    # Transform the target to the smaller of t and its complement S‑t.
    # This ensures the extra element we add is non‑negative.
    if t <= S - t:
        t_prime = t
    else:
        t_prime = S - t

    # Compute the extra element K = S - 2 * t_prime (guaranteed >= 0).
    K = S - 2 * t_prime

    # Construct the Partition instance.
    new_numbers = numbers + [K]
    return {"numbers": new_numbers}

