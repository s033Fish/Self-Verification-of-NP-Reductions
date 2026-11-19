"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) instance format is::

    {"universe_size": u, "sets": [[element, ...], ...]}

where the universe consists of the elements ``0 .. u-1``.  We must produce a
Subset Sum instance::

    {"numbers": [a1, a2, ...], "target": t}

such that a sub‑list of ``numbers`` sums to ``t`` iff the original instance has
an exact cover.

**Standard reduction**
----------------------
Use a positional numeral system with base ``B = u + 1``.  For each set ``S`` we
create a number whose ``e``‑th digit (in base ``B``) is ``1`` if ``e ∈ S`` and
``0`` otherwise.  In decimal this number is ``sum_{e in S} B**e``.  Because the
base is larger than the maximum possible digit sum (which is ``1`` for each
position), adding such numbers never creates a carry – the digit‑wise sum is
exactly the ordinary integer sum.

The target number is the one with digit ``1`` in every position, i.e. the sum
``sum_{e=0}^{u-1} B**e``.  Selecting a collection of the constructed numbers
adds a ``1`` to a digit exactly when the corresponding element appears in the
chosen sets.  Therefore the total sum equals the target iff every element
appears exactly once, i.e. the chosen sets form an exact cover.

The reduction runs in polynomial time: we compute at most ``|sets|`` numbers,
each requiring ``O(u)`` arithmetic on Python's arbitrary‑precision integers.

Edge cases:
* ``u = 0`` – the target is ``0`` and the Subset Sum instance is trivially a
  yes‑instance, matching the Exact Cover definition.
* Empty sets produce the number ``0``; they are harmless because they never
  contribute to reaching the target.

The function ``reduce`` implements this transformation.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list of
        lists of ints) describing the Exact Cover problem.

    Returns
    -------
    dict
        A Subset Sum instance with keys ``"numbers"`` (list of non‑negative
        integers) and ``"target"`` (int).
    """

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base larger than any possible digit sum to avoid carries.
    base: int = u + 1

    numbers: List[int] = []
    for s in sets:
        # Compute the number representing set s: sum_{e in s} base**e
        num = 0
        for e in s:
            # Elements are guaranteed to be in 0..u-1 by the problem spec.
            num += pow(base, e)
        numbers.append(num)

    # Target has digit 1 for every element of the universe.
    target = 0
    for e in range(u):
        target += pow(base, e)

    return {"numbers": numbers, "target": target}

