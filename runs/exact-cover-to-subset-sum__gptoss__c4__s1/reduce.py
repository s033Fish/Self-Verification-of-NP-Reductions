"""Reduction from Exact Cover to Subset Sum.

The reduction encodes each set as a number in base B = u + 1, where u is the
size of the universe. For a set S the corresponding number is

    n_S = sum_{e in S} B**e

The target number is the sum of all unit vectors, i.e. the number whose base‑B
representation has a 1 in every digit 0..u-1:

    target = sum_{e=0}^{u-1} B**e

If a collection of sets is pairwise disjoint and covers the whole universe then
the sum of their numbers equals ``target`` (no carries occur because each digit
is at most 1). Conversely, any subset of the numbers that sums to ``target``
must use each digit exactly once, which implies the chosen sets are disjoint
and cover the universe.  This gives a polynomial‑time many‑to‑one reduction.

Edge cases:
* ``u = 0`` – the target is 0. Subset‑Sum with target 0 is always a yes‑instance
  (the empty sub‑list), matching the Exact‑Cover answer.
* Empty sets are encoded as the number 0; they never affect the sum and can be
  safely included.

The function validates the input using ``ExactCover.validate`` and returns a
valid Subset‑Sum instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ExactCover, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    Parameters
    ----------
    instance: dict
        An Exact Cover instance with keys ``"universe_size"`` and ``"sets"``.

    Returns
    -------
    dict
        A Subset Sum instance with keys ``"numbers"`` and ``"target"``.
    """
    # Validate the source instance – will raise InvalidInstance on bad input.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base for the positional encoding. Using u+1 guarantees that any digit
    # sum never reaches the base unless the same element appears in two chosen
    # sets, which would cause a carry and thus a mismatch with the target.
    base: int = u + 1

    # Encode each set as a number.
    numbers: List[int] = []
    for s in sets:
        # Sum base**e for each element e in the set.
        num = 0
        for e in s:
            num += pow(base, e)
        numbers.append(num)

    # Target is the number with a 1 in every digit 0..u-1.
    target = 0
    for e in range(u):
        target += pow(base, e)

    # Validate the produced target instance.
    SubsetSum.validate({"numbers": numbers, "target": target})
    return {"numbers": numbers, "target": target}

