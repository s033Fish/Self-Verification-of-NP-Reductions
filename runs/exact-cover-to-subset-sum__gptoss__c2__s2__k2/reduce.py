"""Reduction from ExactCover to SubsetSum.

ExactCover instance format:
    {"universe_size": u, "sets": [[element, ...], ...]}
SubsetSum instance format:
    {"numbers": [a1, a2, ...], "target": t}

The reduction encodes each set as a number in a large base B = m+1,
where m is the number of sets.  The i‑th digit (base B) corresponds to
universe element i and is 1 iff the set contains that element.  Because
B > m, the sum of any collection of such numbers cannot cause a carry
between digits.  Hence a subset of numbers sums to the target
    sum_{i=0}^{u-1} B^i
iff each digit sums to exactly 1, i.e., the chosen sets form an exact
cover.
"""

def reduce(instance):
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance: dict
        ExactCover instance with keys "universe_size" and "sets".

    Returns
    -------
    dict
        SubsetSum instance with keys "numbers" and "target".
    """
    u = instance.get("universe_size", 0)
    sets = instance.get("sets", [])
    m = len(sets)
    # Base larger than the maximum possible coefficient per digit
    B = m + 1
    numbers = []
    for s in sets:
        # Compute the encoded number for this set
        val = 0
        for e in s:
            # e is assumed to be in 0..u-1
            val += pow(B, e)
        numbers.append(val)
    # Target is the sum of B^i for all universe elements
    target = sum(pow(B, i) for i in range(u))
    return {"numbers": numbers, "target": target}

# The module exposes only the reduce function as required by the
# evaluation harness.

__all__ = ["reduce"]

