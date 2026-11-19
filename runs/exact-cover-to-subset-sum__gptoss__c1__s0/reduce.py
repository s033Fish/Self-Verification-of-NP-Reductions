"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) is defined as:
    instance = {"universe_size": u, "sets": [[e1, e2, ...], ...]}
    The universe consists of elements 0 .. u-1.  We ask whether a sub‑collection
    of the given sets forms a partition of the universe – i.e. the chosen
    sets are pairwise disjoint and their union is the whole universe.

The target problem (SubsetSum) is defined as:
    instance = {"numbers": [a1, a2, ...], "target": t}
    We ask whether a sub‑list of ``numbers`` sums exactly to ``t``.

We implement a classic polynomial‑time many‑one reduction using a positional
encoding with a base larger than any possible digit overflow.  Let
    B = u + 1.
For a set S we create the number
    value(S) = Σ_{e ∈ S} B**e.
The target value is the sum of all powers of B up to u‑1:
    T = Σ_{e=0}^{u-1} B**e.

If the Exact Cover instance is a *yes* instance, the selected sets are
disjoint and contain each element exactly once, therefore the sum of their
corresponding numbers equals T.  Conversely, any subset of the numbers that
adds up to T must contribute exactly one copy of each power B**e, because a
 digit 2 in any position would already exceed T (B > 1 and B**e > Σ_{i<e}B**i).
Thus the subset corresponds to a collection of pairwise disjoint sets covering
the whole universe.

The construction runs in time polynomial in the size of the input (O(u·|sets|))
and uses only integer arithmetic.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
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
    u: int = instance.get("universe_size", 0)
    sets: List[List[int]] = instance.get("sets", [])

    # Base for positional encoding.  Using u+1 guarantees that a carry cannot
    # turn a digit 2 into a valid representation of the target.
    base: int = u + 1

    # Compute the number for each set.
    numbers: List[int] = []
    for s in sets:
        # Skip empty sets – they contribute 0 and never affect the sum.
        if not s:
            numbers.append(0)
            continue
        val = 0
        for e in s:
            # Elements are guaranteed to be in 0..u-1 by the problem spec.
            val += pow(base, e)
        numbers.append(val)

    # Target is the sum of all powers base**e for e = 0 .. u-1.
    target = 0
    for e in range(u):
        target += pow(base, e)

    return {"numbers": numbers, "target": target}

