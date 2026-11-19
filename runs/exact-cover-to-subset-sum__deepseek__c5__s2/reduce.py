"""Polynomial-time reduction from Exact Cover to Subset Sum.

Source (ExactCover): {"universe_size": u, "sets": [[element, ...], ...]}
Target (SubsetSum):  {"numbers": [a1, a2, ...], "target": t}

Idea
----
Choose a base B strictly larger than the number of sets m.  Encode each
universe element as a digit position.  For set S_j define the number

    a_j = sum over e in S_j of B**e

so its base-B representation has a 1 exactly at the positions of the
elements it contains (and 0 elsewhere).  Let the target be

    t = sum over e in 0..u-1 of B**e

i.e. the base-B number with a 1 in every one of the u digit positions.

Because each a_j has digits in {0,1} and at most m numbers are ever added,
every digit column of any sub-list sum is at most m < B.  Hence there are
no carries in base B: a sub-list sums to t exactly when, for every element
e, exactly one chosen set contains e.  That is precisely an exact cover.

Notes / edge cases
------------------
* u = 0 gives target 0, so the empty sub-list is a valid witness (yes).
* Empty sets become the number 0; including them is harmless.
* Two copies of the same non-empty set cannot both be chosen: some digit
  column would become 2, which cannot appear in t without a carry.
* The construction uses O(u * m) digit operations; the resulting integers
  have O(u * log m) bits, polynomial in the input size.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Exact Cover instance to a Subset Sum instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    # Base must exceed the maximum possible digit sum, which is at most the
    # number of chosen sets <= m.  B = m + 1 guarantees no carries; clamp to
    # at least 2 so that the base is a valid positional base even when m = 0.
    m = len(sets)
    base = max(2, m + 1)

    # Powers B**e for e = 0 .. universe_size - 1.
    powers = [base ** e for e in range(universe_size)]

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    target = sum(powers)

    return {"numbers": numbers, "target": target}
