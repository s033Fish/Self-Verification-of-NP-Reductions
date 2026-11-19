"""Polynomial-time reduction from Exact Cover to Subset Sum.

Given an Exact Cover instance with universe size u and a list of m sets,
encode each universe element i as the base-B digit position i, where
B = max(2, m + 1).  The number for a set S is sum_{i in S} B**i, and the
target is sum_{i=0}^{u-1} B**i (i.e. the digit 1 in every position).

Because at most m numbers are selected, no digit column can reach B, so
there are no carries.  A sub-list therefore sums to the target exactly
when every digit column receives exactly one 1, i.e. when the chosen sets
are pairwise disjoint and cover the whole universe.  Empty sets become 0
and are harmless; duplicate non-empty sets cannot both be chosen because
their shared digit would become 2.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    base = max(2, len(sets) + 1)

    # powers[i] = base ** i
    powers = [1] * (universe_size + 1)
    for i in range(1, universe_size + 1):
        powers[i] = powers[i - 1] * base

    numbers = []
    for s in sets:
        value = 0
        for element in s:
            value += powers[element]
        numbers.append(value)

    # sum_{i=0}^{u-1} base**i = (base**u - 1) // (base - 1)
    target = (powers[universe_size] - 1) // (base - 1)

    return {"numbers": numbers, "target": target}
