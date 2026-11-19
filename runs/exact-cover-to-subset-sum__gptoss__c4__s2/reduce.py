"""Reduction from Exact Cover to Subset Sum.

The reduction uses a positional numeral system with base B = u + 1, where u is
the size of the universe.  For each element i in the universe we assign the
value B**i.  The value of a set is the sum of the values of its elements.  The
target value is the sum of B**i for all i in the universe.

Because each digit in this base representation is strictly smaller than the
base, adding the values of two sets that share an element would produce a digit
≥ B, which cannot be cancelled by any combination of other set values.  Hence a
subset of sets sums to the target exactly when the chosen sets are pairwise
disjoint and their union covers the whole universe – i.e. when they form an
exact cover.

The construction runs in polynomial time: we compute B = u + 1 and then a
single exponentiation per element of each set.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ExactCover, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Map an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary representing an ExactCover instance.  It must contain the
        keys ``"universe_size"`` (an int ≥ 0) and ``"sets"`` (a list of lists
        of ints).  Validation is performed via ``ExactCover.validate``.

    Returns
    -------
    dict
        A SubsetSum instance ``{"numbers": [...], "target": t}`` such that the
        SubsetSum instance is a *yes* instance iff the original ExactCover
        instance is a *yes* instance.
    """
    # Validate the source instance.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base for the positional representation.  Using u+1 guarantees that each
    # digit is strictly smaller than the base, preventing carries.
    base: int = u + 1

    # Pre‑compute powers of the base to avoid repeated exponentiation.
    # pow_cache[i] = base**i for i in 0..u-1.
    pow_cache = [pow(base, i) for i in range(u)]

    # Convert each set into a single integer value.
    numbers: List[int] = []
    for s in sets:
        # Empty sets contribute 0 and are irrelevant for the sum; we can keep
        # them or drop them – SubsetSum tolerates zeros.
        total = 0
        for elem in s:
            total += pow_cache[elem]
        numbers.append(total)

    # Target is the sum of all base powers, i.e., the representation with a 1
    # in each digit position.
    target = sum(pow_cache)

    result = {"numbers": numbers, "target": target}
    # Validate the produced SubsetSum instance before returning.
    SubsetSum.validate(result)
    return result
