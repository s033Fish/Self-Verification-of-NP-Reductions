"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) is defined by an instance of the form::

    {"universe_size": u, "sets": [[e0, e1, ...], ...]}

where the universe consists of the elements ``0 .. u-1``.  The question is
whether we can pick a sub‑collection of the given sets that are pairwise
disjoint and whose union is the whole universe.

The target problem (SubsetSum) expects an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

and asks whether a sub‑list of ``numbers`` sums exactly to ``t``.

The classic polynomial‑time reduction encodes each set as a number written in
base ``B = u + 1``.  For a set ``S`` we create the integer

    val(S) = Σ_{i ∈ S} B^i

Because ``B`` is larger than the maximum possible digit sum (at most ``u``),
adding such numbers never produces a carry.  Consequently, a collection of
sets sums to the number ``Σ_{i=0}^{u-1} B^i`` iff the sets are disjoint and
cover every element exactly once – precisely the definition of an exact cover.

The reduction runs in time polynomial in the size of the Exact Cover instance
and produces a valid Subset Sum instance.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list
        of list of ints) as described in the ExactCover docstring.

    Returns
    -------
    dict
        A Subset Sum instance with keys ``"numbers"`` and ``"target"``.
    """

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base larger than any possible digit sum to avoid carries.
    base: int = u + 1

    numbers: List[int] = []
    for s in sets:
        # Compute the value of this set in the chosen base.
        val = 0
        for elem in s:
            # Each element contributes base**elem to the number.
            val += pow(base, elem)
        numbers.append(val)

    # Target is the sum of base**i for all i in the universe.
    target = sum(pow(base, i) for i in range(u))

    return {"numbers": numbers, "target": target}

