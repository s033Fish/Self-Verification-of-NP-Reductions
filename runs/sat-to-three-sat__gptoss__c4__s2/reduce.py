"""Reduction from SAT to 3‑SAT.

Implements the classic polynomial‑time reduction that converts an arbitrary
CNF formula into an equivalent 3‑CNF formula.  The transformation never
solves the SAT instance; it only introduces fresh variables and rewrites each
clause according to its length.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Sat, ThreeSat


def _unsat_three_sat() -> Dict[str, Any]:
    """A fixed unsatisfiable 3‑SAT instance (three variables, all 8 clauses)."""
    vars_ = [1, 2, 3]
    clauses = []
    for signs in [(s1, s2, s3) for s1 in (1, -1) for s2 in (1, -1) for s3 in (1, -1)]:
        clause = [signs[0] * vars_[0], signs[1] * vars_[1], signs[2] * vars_[2]]
        clauses.append(clause)
    return {"num_vars": 3, "clauses": clauses}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance satisfies the ``ThreeSat`` format and is
    satisfiable exactly when the input instance is.
    """
    # Validate the source instance.
    Sat.validate(instance)

    m: int = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    new_clauses: List[List[int]] = []
    next_var = m + 1  # next fresh variable index

    for clause in original_clauses:
        # Detect tautological clause (contains both v and -v)
        lits_set = set(clause)
        if any(lit != 0 and -lit in lits_set for lit in lits_set):
            continue  # tautology, always satisfied
        # Remove duplicate literals
        lits = list(lits_set)
        k = len(lits)
        if k == 0:
            # Empty clause -> formula unsatisfiable
            return _unsat_three_sat()
        if k == 1:
            l = lits[0]
            y = next_var
            z = next_var + 1
            next_var += 2
            # Four clauses ensuring l must be true
            new_clauses.append([l, y, z])
            new_clauses.append([l, y, -z])
            new_clauses.append([l, -y, z])
            new_clauses.append([l, -y, -z])
        elif k == 2:
            l1, l2 = lits
            y = next_var
            next_var += 1
            # Two clauses equivalent to (l1 ∨ l2)
            new_clauses.append([l1, l2, y])
            new_clauses.append([l1, l2, -y])
        elif k == 3:
            # Already a valid 3‑clause (distinct variables, no tautology)
            new_clauses.append(lits)
        else:
            # k >= 4: chain construction using fresh variables
            # First clause with a fresh y1
            y_prev = next_var
            next_var += 1
            new_clauses.append([lits[0], lits[1], y_prev])
            # Intermediate clauses for literals 3 .. k-2
            for i in range(2, k - 2):
                y_curr = next_var
                next_var += 1
                new_clauses.append([-y_prev, lits[i], y_curr])
                y_prev = y_curr
            # Final clause connecting the last two literals
            new_clauses.append([-y_prev, lits[-2], lits[-1]])

    # If all original clauses were tautologies, the formula is trivially satisfiable.
    if not new_clauses:
        return {"num_vars": 3, "clauses": [[1, 2, 3]]}

    result = {"num_vars": max(m, next_var - 1), "clauses": new_clauses}
    ThreeSat.validate(result)
    return result

