"""Reduction from Exact Cover to Subset Sum.

The source problem is :class:`ExactCover` defined in ``problems.py``.
The target problem is :class:`SubsetSum` defined in the same file.

For an Exact Cover instance we are given a universe ``U = {0, …, u-1}``
and a list ``S`` of subsets of ``U``.  We must decide whether there is a
sub‑collection of ``S`` that partitions the universe – i.e. the selected
sets are pairwise disjoint and their union is ``U``.

We encode this as a Subset Sum instance using a positional (base‑B) encoding.

* Let ``m`` be the number of sets.  Choose ``B = m + 1``.  ``B`` is larger
  than the maximum possible digit sum for any element, guaranteeing that
  when we add the encoded numbers no carries occur.
* For each set ``s`` we create a number ``n_s = Σ_{e in s} B**e``.  The ``e``‑th
  digit (in base ``B``) is ``1`` iff the set contains element ``e``.
* The target number is ``T = Σ_{e=0}^{u-1} B**e`` – every digit is ``1``.

If a collection of sets covers each element exactly once, the digit‑wise sum
of the corresponding numbers equals ``T``.  If any element is covered zero
or more than once, the digit for that element will be ``0`` or ``≥2``;
because ``B`` exceeds the maximum possible sum, this cannot be compensated
by carries, and the total sum differs from ``T``.

The construction runs in time polynomial in the size of the Exact Cover
instance (the exponentiation uses Python's built‑in ``pow`` which is fast
enough for the small integers we handle).  The produced Subset Sum instance
conforms to the validation rules of ``SubsetSum``.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import ExactCover, SubsetSum

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary representing an Exact Cover instance.  It must pass
        ``ExactCover.validate``.

    Returns
    -------
    dict
        A Subset Sum instance ``{"numbers": [...], "target": t}`` such that
        the Subset Sum instance is a *yes* instance iff the original Exact
        Cover instance is a *yes* instance.
    """
    # Validate the source instance (will raise if malformed).
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    m = len(sets)
    # Base larger than the maximum possible digit sum (which is at most m).
    base = m + 1  # base >= 1; when m = 0 (no sets) base = 1 works fine.

    numbers: List[int] = []
    for s in sets:
        # Encode each set as a number in the chosen base.
        num = 0
        for e in s:
            # e is guaranteed to be in 0..u-1 by validation.
            num += pow(base, e)
        numbers.append(num)

    # Target: each element digit is 1.
    target = 0
    for e in range(u):
        target += pow(base, e)

    reduced: Dict[str, Any] = {"numbers": numbers, "target": target}
    # Validate the produced instance.
    SubsetSum.validate(reduced)
    return reduced

