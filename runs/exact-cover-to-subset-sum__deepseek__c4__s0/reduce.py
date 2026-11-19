"""Polynomial-time reduction from Exact Cover to Subset Sum.

Encoding
--------
Let the Exact Cover instance have universe 0..u-1 and m sets S_0..S_{m-1}.
Choose base b = m + 1.  Map element i to the "digit position" i, and map a
set S to the integer

    value(S) = sum_{i in S} b^i .

The target is

    t = sum_{i=0}^{u-1} b^i

i.e. the number whose base-b representation is all ones in the u low
positions.

Why it works
------------
Every set contributes at most one b^i for each element i (elements of a set
are distinct), so in any sub-collection of the numbers the base-b digit at
position i is the number of chosen sets containing i, which is between 0 and
m < b.  Hence there are no carries: a sub-collection sums to t iff every digit
equals 1, i.e. iff the chosen sets are pairwise disjoint and cover every
element of the universe exactly once.  Empty sets become the number 0 and
never change a sum, matching the fact that they never matter.  For u = 0 the
target is 0, which the empty sub-list realises.

The numbers produced have O(u) base-b digits with b = m+1, so the output size
is polynomial in the input size (u * m digits, each O(log m) bits).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an ExactCover instance to a SubsetSum instance."""
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)

    base = m + 1

    # powers[i] = base ** i for i in 0..u-1
    powers = [1] * u
    for i in range(1, u):
        powers[i] = powers[i - 1] * base

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    target = sum(powers)  # sum_{i=0}^{u-1} base**i

    return {"numbers": numbers, "target": target}
