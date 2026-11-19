"""Polynomial-time reduction from Exact Cover to Subset Sum.

Encoding
--------
Let u be the universe size and m the number of sets.  Pick a base
B = m + 1.  For element i (0 <= i < u) reserve the i-th "digit" of a
base-B number.  Map each set S to the number

    a(S) = sum_{i in S} B^i

and let the target be

    t = sum_{i=0}^{u-1} B^i = (B^u - 1) / (B - 1)   (for B > 1).

A sub-list of the numbers sums to t exactly when, in every digit
position i, the chosen sets contribute exactly one B^i.  Because at most
m sets are chosen and each contributes at most 1 to any digit, every
digit sum is at most m < B, so there are no carries between digits.
Hence digit i of the sum is 1 iff exactly one chosen set contains
element i.  Therefore the sum equals t iff the chosen sets are pairwise
disjoint and cover the whole universe -- i.e. iff the Exact Cover
instance is a yes-instance.

Edge cases:
  * u = 0: t = 0, and the empty sub-list (or any empty sets, which map
    to 0) sums to 0, so the answer is yes.
  * Empty sets map to the number 0 and never change a sum, matching the
    fact that they never matter.
  * Two copies of the same non-empty set map to the same number; using
    both would put a 2 in some digit, which cannot equal the target's 1.
  * m = 0: B = 1 and there are no numbers; t = u, which is achievable
    only when u = 0.  This matches "yes iff the universe is empty".

The output is polynomial in the input size: there are m numbers, each
with u base-B digits, so O(m * u * log m) bits.  The powers B^i are
computed incrementally, so the running time is polynomial as well.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Exact Cover instance to a Subset Sum instance."""
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)

    base = m + 1

    # powers[i] = base ** i, computed incrementally.
    powers: list[int] = [1] * u
    for i in range(1, u):
        powers[i] = powers[i - 1] * base

    numbers: list[int] = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    if base == 1:
        # No sets at all (m == 0); the only achievable sum is 0.
        target = u
    else:
        target = sum(powers)  # = (base ** u - 1) // (base - 1)

    return {"numbers": numbers, "target": target}
