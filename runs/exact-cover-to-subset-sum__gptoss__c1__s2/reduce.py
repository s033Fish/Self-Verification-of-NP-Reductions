"""Reduction from Exact Cover to Subset Sum.

The source problem **ExactCover** is defined as:

*Instance*: {"universe_size": u, "sets": [[element, ...], ...]}
    * The universe consists of the elements 0 .. u-1.
    * Each set lists distinct elements of the universe.  Sets may be empty
      and duplicates are allowed.
    * An exact cover exists iff we can pick some of the sets such that they
      are pairwise disjoint and their union equals the whole universe.
    * Edge case: u = 0 is a *yes* instance (choose no sets).

The target problem **SubsetSum** is defined as:

*Instance*: {"numbers": [a1, a2, ...], "target": t}
    * numbers are non‑negative integers (repetitions allowed).
    * target is any integer.
    * A *yes* instance exists iff a sub‑list of numbers sums exactly to t.
    * Edge case: t = 0 is always *yes* (empty sub‑list).

The classic polynomial‑time reduction encodes each set as a number whose
base‑B representation has a 1 in the digit positions corresponding to the
elements covered by the set and 0 elsewhere.  By choosing B larger than the
maximum possible digit sum (i.e. B = u + 1) we guarantee that no carry can
occur when adding such numbers.  Consequently, a collection of sets covers
each element exactly once iff the sum of the corresponding numbers is
target = B^0 + B^1 + ... + B^{u-1}.

Implementation details
----------------------
* For u = 0 we return an empty numbers list and target = 0 – the Subset‑Sum
  instance is trivially a *yes* instance, matching the Exact‑Cover answer.
* Empty sets map to the number 0; they never affect the sum and can be safely
  included.
* The reduction runs in time polynomial in the size of the Exact‑Cover
  instance: we iterate over each set and each element inside it, performing
  only integer arithmetic.

The function ``reduce`` follows the signature required by the evaluation
framework: it receives a dictionary representing an Exact‑Cover instance and
returns a dictionary representing a Subset‑Sum instance.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys "universe_size" (int) and "sets" (list of
        lists of ints) following the specification of ExactCover.

    Returns
    -------
    dict
        A Subset‑Sum instance with keys "numbers" and "target".
    """

    u: int = int(instance.get("universe_size", 0))
    sets: List[List[int]] = instance.get("sets", [])

    # Edge case: empty universe – target 0, any numbers (including none) work.
    if u == 0:
        return {"numbers": [], "target": 0}

    # Choose a base larger than the maximum possible digit sum to avoid carries.
    # Using B = u + 1 guarantees that adding any subset of the numbers never
    # creates a carry because each digit position can receive at most one "1"
    # from each selected set, and the total per digit is therefore ≤ number of
    # sets ≤ u (since duplicates are irrelevant for the exact cover).
    B: int = u + 1

    numbers: List[int] = []
    for s in sets:
        # Compute the integer representing the set in base B.
        # Empty sets become 0.
        val = 0
        for e in s:
            # Elements are guaranteed to be in 0..u-1 by the problem
            # specification; we do not enforce it here for performance.
            val += pow(B, e)
        numbers.append(val)

    # Target is the sum of B^i for i = 0 .. u-1, i.e., (B**u - 1) // (B - 1).
    target = (pow(B, u) - 1) // (B - 1)

    return {"numbers": numbers, "target": target}

