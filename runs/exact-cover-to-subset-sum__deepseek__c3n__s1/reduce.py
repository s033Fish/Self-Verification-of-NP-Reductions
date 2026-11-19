"""Polynomial-time reduction from Exact Cover to Subset Sum.

Idea (the standard base-encoding reduction)
-------------------------------------------
Let the instance be ``{"universe_size": u, "sets": S_1..S_m}``.  Pick a base
``b = m + 1`` (strictly larger than the number of sets).  Encode a set S as the
integer

    a(S) = sum_{e in S} b^e

and let the target be

    t = sum_{e=0}^{u-1} b^e .

In base b, ``a(S)`` has a 1 in exactly the digit positions belonging to S, and
``t`` has a 1 in every digit position 0..u-1.  A sub-collection of sets has
digit sums at most m < b, so adding the chosen ``a(S)`` produces no carries.
Therefore the sum equals t iff every digit (every universe element) is covered
exactly once, i.e. iff the chosen sets form an exact cover.

Edge cases:
  * u = 0: t = 0, which is always yes (empty sub-list) -- matches Exact Cover.
  * Empty sets encode to 0 and never affect the sum.
  * Duplicate sets are distinct numbers positions; two copies of a non-empty
    set cannot both be chosen because that would make some digit 2, and no
    carry can hide it (2 < b).
  * m = 0: b = 1; then t = u and there are no numbers, so the answer is yes
    only when u = 0, which is correct.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    The returned Subset Sum instance is yes exactly when ``instance`` is yes.
    """
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    m = len(sets)
    base = m + 1

    # Powers b^0 .. b^(u-1).
    powers = [1] * universe_size
    for e in range(1, universe_size):
        powers[e] = powers[e - 1] * base

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    target = sum(powers)

    return {"numbers": numbers, "target": target}
