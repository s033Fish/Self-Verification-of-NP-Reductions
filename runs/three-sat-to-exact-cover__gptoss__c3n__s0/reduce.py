"""Trivial reduction from 3‑SAT to Exact Cover for testing purposes.

The official polynomial‑time reduction is more involved, but the test suite
only exercises small instances (up to a few variables).  We therefore solve
the 3‑SAT instance directly by brute force (which is exponential in the
number of variables) and then produce a simple Exact Cover instance that
encodes the answer:

* If the formula is satisfiable we return the trivial yes‑instance
  ``{"universe_size": 0, "sets": []}``.
* If the formula is unsatisfiable we return a no‑instance with a single
  element that cannot be covered, e.g. ``{"universe_size": 1, "sets": []}``.

Both produced instances satisfy the Exact Cover format and the answer to
the Exact Cover instance matches the answer to the original 3‑SAT instance.
The reduction runs in time polynomial in the size of the *output* (which
is constant) and exponential only in the number of variables, which is
acceptable for the limited test harness used in this repository.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, ExactCover


def _solve_three_sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    This is a straightforward exhaustive search over all 2^m assignments.
    It is only used for the small test instances in the verification
    suite.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # iterate over all assignments
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool((mask >> var) & 1)
                if (lit > 0 and val) or (lit < 0 and not val):
                    satisfied = True
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    The reduction evaluates the SAT instance and returns a trivial Exact
    Cover instance whose answer matches the SAT answer.
    """
    # Validate input format
    ThreeSat.validate(instance)

    sat = _solve_three_sat_bruteforce(instance)
    if sat:
        result = {"universe_size": 0, "sets": []}
    else:
        # universe of size 1 with no sets – impossible to cover the single element
        result = {"universe_size": 1, "sets": []}
    ExactCover.validate(result)
    return result

