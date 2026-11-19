"""Reduction from Exact Cover to Subset Sum.

The reduction encodes each set as a number in a mixed‑radix (base) system.
Let ``u`` be the size of the universe.  Choose ``B = u + 1``.  For a set ``S``
define the number ``n_S = sum(B**i for i in S)``.  The target value is
``T = sum(B**i for i in range(u))``.

Because ``B`` is larger than any digit that can appear (each digit is either
0 or 1), adding numbers corresponding to *disjoint* sets never creates a carry.
Consequently a sub‑set of the numbers sums to ``T`` exactly when the chosen
sets are pairwise disjoint and their union is the whole universe – i.e. they
form an exact cover.  The construction is polynomial‑time: we perform a linear
pass over the input and use Python's built‑in big integers for exponentiation.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ExactCover, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to ``ExactCover.validate`` – it contains the
        keys ``"universe_size"`` (non‑negative int) and ``"sets"`` (list of
        lists of element indices).

    Returns
    -------
    dict
        An instance suitable for ``SubsetSum.validate`` – a dictionary with
        keys ``"numbers"`` (list of non‑negative ints) and ``"target"`` (int).
    """
    # Ensure the source instance is well‑formed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base larger than any possible digit (0/1). Using u+1 guarantees that
    # carries never happen when adding numbers representing disjoint sets.
    base = u + 1

    # Pre‑compute powers of the base for efficiency.
    powers = [base ** i for i in range(u)]

    numbers: List[int] = []
    for s in sets:
        # Empty sets contribute nothing and can be omitted.
        if not s:
            continue
        # Encode the set as a number.
        num = sum(powers[i] for i in s)
        numbers.append(num)

    target = sum(powers)

    # Validate the produced SubsetSum instance before returning.
    SubsetSum.validate({"numbers": numbers, "target": target})
    return {"numbers": numbers, "target": target}

