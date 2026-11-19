"""Polynomial-time reduction from Exact Cover to Subset Sum.

Given an Exact Cover instance with universe 0..u-1 and m sets, pick a base
b > m (b = max(m + 1, 2)).  Encode each set S as the number

    a(S) = sum_{e in S} b^e

and let the target be

    t = sum_{e=0}^{u-1} b^e.

Because every digit of every number is 0 or 1 and at most m numbers are
chosen, no digit of a sub-list sum ever reaches b, so there are no carries.
Thus a sub-list sums to t exactly when, for every element e, exactly one
chosen set contains e -- i.e. exactly when the chosen sets form an exact
cover.  Empty sets become the number 0 and never help; duplicate sets are
distinct positions, and choosing both would put a 2 in a shared element
digit, which cannot equal the target's 1.

The construction is polynomial: b has O(log m) bits and each b^e has
O(u log m) bits, so the output size is O(m u log m) bits.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    base = max(len(sets) + 1, 2)

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += base ** element
        numbers.append(value)

    target = 0
    for element in range(universe_size):
        target += base ** element

    return {"numbers": numbers, "target": target}
