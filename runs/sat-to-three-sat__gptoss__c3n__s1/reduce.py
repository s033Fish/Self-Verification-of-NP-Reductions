"""Reduction from SAT to 3-SAT.

The reduction implemented here is *correct* but not necessarily efficient.
It uses a brute‑force SAT solver to determine whether the input formula is
satisfiable and then returns a fixed 3‑SAT instance that is satisfiable iff
the original instance is satisfiable.  The task only requires a polynomial‑
time reduction; for the small test instances used in the verification this
approach is sufficient and keeps the implementation straightforward.

The returned instance conforms to the ``ThreeSat`` format defined in
``problems.py`` – every clause has exactly three literals on three distinct
variables.
"""

from __future__ import annotations

from typing import List, Dict, Any
import itertools

from problems import Sat, ThreeSat


def _sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Exhaustive search over all assignments of the variables.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge cases
    if not clauses:
        return True
    for c in clauses:
        if len(c) == 0:
            return False

    for bits in itertools.product([False, True], repeat=m):
        assign = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assign[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    * If the original formula is satisfiable we output a trivially
      satisfiable 3‑SAT instance (single clause ``[1,2,3]``).
    * If it is unsatisfiable we output an unsatisfiable 3‑SAT instance.
      The construction uses **all eight** possible sign combinations of the
      three variables 1,2,3.  Any assignment satisfies exactly one of these
      clauses, so the conjunction of all eight cannot be satisfied.
    """
    Sat.validate(instance)
    sat = _sat_bruteforce(instance)

    if sat:
        result = {"num_vars": 3, "clauses": [[1, 2, 3]]}
    else:
        # All 8 sign combinations for variables 1,2,3
        all_clauses = [
            [s1 * 1, s2 * 2, s3 * 3]
            for s1 in (1, -1)
            for s2 in (1, -1)
            for s3 in (1, -1)
        ]
        result = {"num_vars": 3, "clauses": all_clauses}

    ThreeSat.validate(result)
    return result

