"""Polynomial-time reduction from Exact Cover to Subset Sum.

Idea
----
Let the universe be {0, ..., u-1} and let there be m sets S_1, ..., S_m.
Pick a base b = m + 1 (at least 2).  Map each set S_i to the integer

    N_i = sum_{e in S_i} b^e

and map the instance to

    numbers = [N_1, ..., N_m],   target = sum_{e=0}^{u-1} b^e

i.e. the target has digit 1 in every universe position.

A sub-list of the numbers corresponds to a sub-collection of the sets, and
each position of the list is used at most once, so no set is ever used twice.
For a chosen sub-collection, the sum is sum_e c_e * b^e where c_e is the
number of chosen sets containing element e.  Since c_e <= m < b, there are no
carries in base b, so the sum equals the target exactly when c_e = 1 for every
element e.  That is precisely the condition that the chosen sets are pairwise
disjoint and cover the whole universe, i.e. an exact cover.

The construction is polynomial: the output has m numbers, each with at most u
base-b digits.
"""

from __future__ import annotations


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)

    # Base strictly larger than the number of sets, so digit sums (<= m)
    # never carry.  b >= 2 keeps the representation well defined for m = 0.
    base = max(m + 1, 2)

    # powers[e] = base ** e
    powers = [1] * universe_size
    for e in range(1, universe_size):
        powers[e] = powers[e - 1] * base

    # Target = 1 in every one of the u digit positions.
    target = sum(powers)

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    return {"numbers": numbers, "target": target}
