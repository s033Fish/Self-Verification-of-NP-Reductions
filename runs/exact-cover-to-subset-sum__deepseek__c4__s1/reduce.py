"""Polynomial-time reduction from Exact Cover to Subset Sum.

Idea (base encoding / no-carry trick):
    Let m be the number of sets and B = m + 1.  Encode a set S as the integer
        value(S) = sum_{i in S} B^i .
    Let the target be
        T = sum_{i=0}^{u-1} B^i .
    Any element i appears in at most m of the sets, so in any sub-collection the
    "digit" at position i (in base B) is at most m < B: there are no carries.
    Hence a sub-collection of sets sums to T exactly when every digit equals 1,
    i.e. every universe element is covered exactly once -- an exact cover.

The encoding is polynomial in the input size (each number has u base-B digits,
B <= m+1), and the construction itself is polynomial.
"""

from __future__ import annotations

import sys
from typing import Any

# The target format allows integers of any size.  Python caps int<->str
# conversion by default, which can make problems.py's validate() raise while
# formatting an error message for a legitimately huge number.  Lift the cap.
try:
    sys.set_int_max_str_digits(0)
except AttributeError:  # pragma: no cover - older Python
    pass


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    base = len(sets) + 1

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
