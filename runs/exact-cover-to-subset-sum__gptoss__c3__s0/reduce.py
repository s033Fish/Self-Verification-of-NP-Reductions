"""Reduction from Exact Cover to Subset Sum.

The reduction uses a mixed-radix encoding to avoid carries when summing numbers.
For a universe of size ``u`` and ``m`` sets we choose a base ``b = m+1``.
Each element ``e`` corresponds to a digit of that base.  A set ``S`` is encoded
as the integer ``sum(b**e for e in S)``.  Because any digit can increase by at
most ``m`` (the total number of selected sets containing that element), using
base ``b`` guarantees that adding any subset of the encoded numbers never
produces a carry into the next digit.

The target is the integer whose every digit is ``1``: ``sum(b**e for e in
range(u))``.  A subset of numbers sums to the target exactly when each digit
adds up to ``1``, i.e. each universe element appears in exactly one chosen set.
Thus the Subset‑Sum instance is a yes‑instance iff the original Exact‑Cover
instance has an exact cover.

Edge cases are handled automatically:
* ``u = 0`` → target ``0``.  The empty sub‑list always sums to ``0``.
* Empty sets encode to ``0`` and never affect the sum.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ExactCover, SubsetSum


def reduce(instance: Dict) -> Dict:
    """Reduce an Exact Cover instance to a Subset Sum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ExactCover format:
        ``{"universe_size": u, "sets": [[e, ...], ...]}``.

    Returns
    -------
    dict
        A SubsetSum instance ``{"numbers": [...], "target": t}`` where the
        answer is yes iff the original ExactCover instance is a yes‑instance.
    """
    # Validate source instance.
    ExactCover.validate(instance)

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Mixed‑radix encoding to avoid carries.
    m = len(sets)
    base = m + 1  # base > maximum possible digit sum

    numbers: List[int] = []
    for s in sets:
        num = 0
        for e in s:
            num += base ** e
        numbers.append(num)

    # Target: digit 1 in each of the first u positions.
    target = sum(base ** e for e in range(u))

    # Validate produced instance (optional).
    SubsetSum.validate({"numbers": numbers, "target": target})

    return {"numbers": numbers, "target": target}

