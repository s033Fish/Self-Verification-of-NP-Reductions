"""Polynomial-time reduction from Exact Cover to Subset Sum.

Exact Cover instance:
    {"universe_size": u, "sets": [[element, ...], ...]}

Subset Sum instance:
    {"numbers": [a1, a2, ...], "target": t}

Reduction
---------
Let m be the number of sets and choose the base b = m + 1.  Encode a set S
as the integer

    a(S) = sum_{e in S} b**e

and let the target be

    t = sum_{e=0}^{u-1} b**e .

Every set contributes at most one to each base-b digit, and at any digit the
total contribution is at most m < b, so adding the chosen numbers produces
no carries between digits.  Therefore a sub-list sums to t exactly when each
base-b digit of the sum is 1, i.e. when the chosen sets are pairwise disjoint
and cover every element of the universe exactly once.

Empty sets become the number 0 and never affect the sum, matching the fact
that they are irrelevant to Exact Cover.  Repeated copies of a non-empty set
become repeated positive numbers; choosing two copies would make some digit
equal to 2 and hence cannot yield the target.  For u = 0 the target is 0 and
the empty sub-list is a valid solution, so the answer is yes as required.

The construction uses O(m * u) base-b digits, i.e. polynomial output size,
and performs only polynomial-time integer arithmetic.
"""


def reduce(instance):
    """Return a Subset Sum instance that is yes iff ``instance`` is yes."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    base = len(sets) + 1

    powers = [1] * universe_size
    for e in range(1, universe_size):
        powers[e] = powers[e - 1] * base

    numbers = [sum(powers[e] for e in subset) for subset in sets]
    target = sum(powers)

    return {"numbers": numbers, "target": target}
