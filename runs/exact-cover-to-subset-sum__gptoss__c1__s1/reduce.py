"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) instance format:
    {"universe_size": u, "sets": [[element, ...], ...]}

The target problem (SubsetSum) instance format:
    {"numbers": [a1, a2, ...], "target": t}

We use a classic base‑encoding reduction.  Choose a base B = u + 1.
For each set S we create a number whose i‑th digit (in base B) is 1
iff i ∈ S and 0 otherwise.  This number is simply:
    a_S = Σ_{i ∈ S} B**i
The target number is the sum of all unit‑vectors, i.e. each element
appears exactly once:
    t = Σ_{i=0}^{u-1} B**i

Because B > 1 and any digit sum in a valid exact cover is at most 1,
no carries occur when adding the chosen numbers.  Hence a sub‑set of the
generated numbers sums to t exactly when the corresponding sets are a
disjoint cover of the universe.

Edge cases:
* If u == 0 the target is 0 and the answer is always yes (empty cover).
* Empty sets translate to the number 0, which never affects the sum and
  can safely be included.

The reduction runs in polynomial time: we compute B**i for i up to u‑1
once and then construct each number by summing the appropriate powers.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance: dict
        ExactCover instance with keys ``"universe_size"`` and ``"sets"``.

    Returns
    -------
    dict
        SubsetSum instance with keys ``"numbers"`` and ``"target"``.
    """
    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Base larger than any possible digit sum to avoid carries.
    base: int = u + 1

    # Pre‑compute powers of the base up to u‑1.
    powers: List[int] = [pow(base, i) for i in range(u)]

    numbers: List[int] = []
    for s in sets:
        # Sum the powers corresponding to elements in the set.
        # Elements are guaranteed to be in 0..u-1 by the problem spec.
        total = 0
        for elem in s:
            if 0 <= elem < u:
                total += powers[elem]
        numbers.append(total)

    # Target is the sum of all unit vectors (each element exactly once).
    target: int = sum(powers)

    return {"numbers": numbers, "target": target}

