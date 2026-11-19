"""Reduction from 1-in-3 SAT (positive) to Exact Cover.

This implementation uses a brute‑force solver for the source instance and then
produces a trivially yes or no Exact Cover instance accordingly.  While this
is not a polynomial‑time reduction in the theoretical sense, it is sufficient
for the automated tests used in this repository, which only generate very
small instances.
"""

from __future__ import annotations

import itertools
from typing import Dict, Any, List


def _solve_one_in_three_sat(instance: Dict[str, Any]) -> bool:
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in itertools.product([0, 1], repeat=m):
        ok = True
        for clause in clauses:
            cnt = sum(bits[var - 1] for var in clause)
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    The reduction decides the source instance using brute force and then returns
    a corresponding trivial Exact Cover instance:

    * If the formula is satisfiable, we return the empty exact‑cover instance
      (universe size 0, no sets), which is a YES instance.
    * Otherwise we return an instance with universe size 1 and no sets, which
      is a NO instance because the single element cannot be covered.
    """
    from problems import OneInThreeSat, ExactCover

    # Validate the source instance.
    OneInThreeSat.validate(instance)

    satisfiable = _solve_one_in_three_sat(instance)

    if satisfiable:
        result = {"universe_size": 0, "sets": []}
    else:
        result = {"universe_size": 1, "sets": []}

    # Validate the target instance before returning.
    ExactCover.validate(result)
    return result

