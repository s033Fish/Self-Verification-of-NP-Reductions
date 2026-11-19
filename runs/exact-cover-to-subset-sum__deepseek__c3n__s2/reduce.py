"""Polynomial-time reduction from Exact Cover to Subset Sum.

Encoding
--------
Let the instance have universe size u and m sets.  Choose base B = m + 1 and
give element i the place value B**i.  Map set S_j to the number

    a_j = sum_{i in S_j} B**i

and the target to

    T = sum_{i=0}^{u-1} B**i .

Because a sub-collection uses at most m sets, every base-B digit of any
achievable sum is at most m < B, so there are never any carries between
digits.  A sub-collection sums to T iff, for every element i, exactly one
chosen set contains i -- that is, iff the chosen sets form an exact cover.

Edge cases:
  * u = 0  -> T = 0 and every a_j = 0, so the empty sub-list works (yes).
  * empty sets map to 0 and never change a sum, matching "empty sets never
    matter".
  * two copies of the same non-empty set would give some digit 2, so they
    cannot both be used, matching the exact-cover rule.
  * m = 0 gives B = 1 and T = u; the number list is empty, which is yes iff
    u = 0, again correct.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Exact Cover instance to a Subset Sum instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    m = len(sets)
    base = m + 1

    # place_values[i] = base ** i
    place_values = [1] * universe_size
    for i in range(1, universe_size):
        place_values[i] = place_values[i - 1] * base

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += place_values[element]
        numbers.append(value)

    target = sum(place_values)
    return {"numbers": numbers, "target": target}
