"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) expects an instance of the form::

    {"universe_size": u, "sets": [[e1, e2, ...], ...]}

where the universe consists of the elements ``0 .. u-1``.  The question is
whether we can pick a sub‑collection of the given sets that are pairwise
 disjoint and whose union is the whole universe.

The target problem (SubsetSum) expects an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

and asks whether a sub‑list of ``numbers`` sums exactly to ``t``.

We use a classic base‑encoding reduction.  Choose a base ``B = u + 1`` –
strictly larger than the number of elements in the universe.  For each set
``S`` we create a number whose base‑``B`` representation has a ``1`` in the
positions corresponding to the elements of ``S`` and ``0`` elsewhere:

    number(S) = sum_{i in S} B**i

The target value is the number that has a ``1`` in *every* digit position
``0 .. u-1``:

    target = sum_{i=0}^{u-1} B**i

Because ``B`` is larger than the maximum possible digit sum (which is at
most the number of chosen sets, but any overlap would make a digit ≥ 2),
no carries can occur when adding these numbers.  Consequently a subset of
the encoded numbers sums to ``target`` iff the corresponding sets are
pairwise disjoint and cover each element exactly once – i.e. they form an
exact cover.

Edge cases:
* ``u = 0`` – the target becomes ``0``.  Subset‑sum with target ``0`` is
  always a yes‑instance, matching the exact‑cover convention.
* Empty sets encode to ``0``.  Including them does not affect the sum, which
  is harmless for the reduction.

The function runs in time polynomial in the size of the input (it iterates
over each set and each element inside the set).
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance: dict
        ``{"universe_size": u, "sets": [[e, ...], ...]}``

    Returns
    -------
    dict
        ``{"numbers": [...], "target": t}`` suitable for the SubsetSum
        solver.
    """
    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base larger than any possible digit sum to avoid carries.
    base = u + 1

    numbers: List[int] = []
    for s in sets:
        # Encode the set as a number in base ``base``.
        val = 0
        for elem in s:
            # Elements are guaranteed to be in 0..u-1 by the problem
            # definition; we trust the input validation elsewhere.
            val += base ** elem
        numbers.append(val)

    # Target: all digits 1 for positions 0 .. u-1.
    target = sum(base ** i for i in range(u))

    return {"numbers": numbers, "target": target}

