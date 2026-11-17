"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[a, b, c], ...]} where every
clause has three distinct positive variables and is satisfied iff exactly one
of a, b, c is true.

Target instance: {"num_vars": M, "clauses": [[l1, l2, l3], ...]} where every
clause has three literals on three distinct variables and is satisfied iff at
least one literal is true.

Reduction
---------
A 1-in-3 clause (a, b, c) means "exactly one of a, b, c is true", i.e.

    (a v b v c)  and  not(a and b) and not(a and c) and not(b and c).

The ternary clause is already a legal 3-SAT clause.  Each binary clause
(~a v ~b) is turned into two legal ternary clauses using a fresh variable x:

    (~a v ~b v x) and (~a v ~b v ~x).

For any assignment to a and b, this pair is satisfiable (for a suitable x)
exactly when ~a v ~b holds: if a and b are both true it forces x and ~x, and
otherwise ~a v ~b satisfies both clauses regardless of x.  Hence the pair is
equivalent to the binary clause.

Each source clause uses three fresh variables, so the target has
M = m + 3 * (number of source clauses) variables, which is polynomial.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a 1-in-3-SAT instance to a 3-SAT instance.

    The returned formula is satisfiable iff the input is 1-in-3 satisfiable.
    Runs in polynomial time in the size of the input.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = m + 1
    out_clauses: list[list[int]] = []

    for a, b, c in clauses:
        # At least one of a, b, c is true.
        out_clauses.append([a, b, c])

        # At most one of a, b, c is true: forbid each pair.
        for u, v in ((a, b), (a, c), (b, c)):
            x = next_var
            next_var += 1
            out_clauses.append([-u, -v, x])
            out_clauses.append([-u, -v, -x])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
