"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) asks for a collection of pairwise disjoint
sets whose union is the whole universe {0,…,u‑1}.  The target problem (SubsetSum)
asks for a sub‑list of numbers that adds up to a given target.

We encode each set as a number written in base ``B = u + 1`` where the digit in
position ``e`` (0‑based) is ``1`` iff the set contains element ``e``.  Because
the base is larger than the maximum possible digit (which is at most the
number of chosen sets covering an element, i.e. ``1`` in a valid exact cover),
adding numbers corresponding to *disjoint* sets never creates a carry.  Hence a
selection of sets sums to the number whose representation has a ``1`` in every
digit – that number is the target.

Formally, for a set ``S`` we use the number ``n(S) = Σ_{e∈S} B**e`` and the
target ``T = Σ_{e=0}^{u-1} B**e``.  The reduction runs in polynomial time because
the bit‑length of each ``B**e`` is O(e·log B) = O(u·log u), i.e. polynomial in the
size of the input instance.

Edge cases:
* ``u = 0`` – the exact‑cover instance is trivially a YES instance.  We map it
  to the Subset‑Sum instance ``{"numbers": [], "target": 0}``, which is also a
  YES instance (empty sub‑list).
* Empty sets in the Exact‑Cover instance are irrelevant – they become the
  number ``0`` and never affect the sum; they can safely be omitted.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse validation utilities if desired.
from problems import ExactCover, SubsetSum


def _encode_set(elements: List[int], base: int) -> int:
    """Encode a single set as a number in the given base.

    ``elements`` is a list of distinct element indices (0‑based).  The function
    returns ``sum(base**e for e in elements)``.
    """
    total = 0
    for e in elements:
        total += base ** e
    return total


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to a SubsetSum instance.

    The returned instance satisfies ``SubsetSum.is_yes`` iff the original
    ExactCover instance satisfies ``ExactCover.is_yes``.
    """
    # Validate the source instance – this will raise InvalidInstance if malformed.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Edge case: empty universe.
    if u == 0:
        # Target 0 is always reachable with the empty sub‑list.
        return {"numbers": [], "target": 0}

    base = u + 1  # base larger than any possible digit count

    numbers: List[int] = []
    for s in sets:
        if not s:
            # Empty sets contribute nothing and can be omitted.
            continue
        numbers.append(_encode_set(s, base))

    # Compute the target: sum_{e=0}^{u-1} base**e.
    # This is a geometric series: (base**u - 1) // (base - 1).
    target = (pow(base, u) - 1) // (base - 1)

    # Return a valid SubsetSum instance.
    reduced = {"numbers": numbers, "target": target}
    SubsetSum.validate(reduced)  # ensure we produced a correct format
    return reduced

