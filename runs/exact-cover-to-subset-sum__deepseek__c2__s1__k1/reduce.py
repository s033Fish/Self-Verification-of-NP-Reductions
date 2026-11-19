"""Polynomial-time reduction from Exact Cover to Subset Sum.

Given an Exact Cover instance with universe {0, ..., u-1} and m sets,
pick base b = m + 1.  Encode each element e as the value b**e, so a set
S corresponds to the number sum_{e in S} b**e.  The target is the number
whose base-b representation is all ones:

    target = sum_{e=0}^{u-1} b**e

Because every set contains each element at most once, choosing a
sub-collection of sets makes the digit in position e equal to the number
of chosen sets containing e.  At most m sets are chosen and m < b, so no
carry can occur and the base-b representation of the sum is unique.  The
sum equals the target exactly when every digit equals 1, i.e. when the
chosen sets are pairwise disjoint and cover the whole universe.

Special cases:
  * u = 0 gives target 0, and the empty sub-list is a valid solution.
  * Empty sets become the number 0 and never affect the sum.
  * Duplicate non-empty sets cannot both be chosen, since that would put
    a digit at 2 while the target has 1 there.
"""


def reduce(instance):
    """Reduce an Exact Cover instance to a Subset Sum instance."""
    u = instance["universe_size"]
    sets = instance["sets"]

    base = len(sets) + 1

    # powers[e] = b**e, the contribution of element e.
    powers = [1] * u
    for e in range(1, u):
        powers[e] = powers[e - 1] * base

    numbers = []
    for s in sets:
        value = 0
        for e in s:
            value += powers[e]
        numbers.append(value)

    target = sum(powers)  # 0 when u == 0

    return {"numbers": numbers, "target": target}
