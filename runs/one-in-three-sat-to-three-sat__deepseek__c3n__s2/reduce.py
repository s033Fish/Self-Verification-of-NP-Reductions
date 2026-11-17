"""Polynomial-time reduction from 1-in-3-SAT (positive) to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[a, b, c], ...]} where every
clause lists 3 distinct positive variables and is satisfied iff EXACTLY ONE
of a, b, c is true.

Target instance: {"num_vars": m', "clauses": [[l1, l2, l3], ...]} where each
clause has 3 literals on 3 distinct variables and is satisfied iff at least
one literal is true.

Reduction
---------
For each source clause (a, b, c) we introduce three fresh variables
x1, x2, x3 and emit seven target clauses:

    ( a  v  b  v  c )                 # at least one of a,b,c is true
    (-a  v -b  v  x1)                 # at most one of a,b is true
    (-a  v -b  v -x1)
    (-a  v -c  v  x2)                 # at most one of a,c is true
    (-a  v -c  v -x2)
    (-b  v -c  v  x3)                 # at most one of b,c is true
    (-b  v -c  v -x3)

The pairs of clauses with a fresh variable are together equivalent to the
two-literal clause (-a v -b) etc.: if both a and b are true then x1 must be
both true and false, which is impossible; otherwise x1 can be chosen to
satisfy both clauses.  Hence the seven clauses are satisfiable exactly when
exactly one of a, b, c is true.  Clauses are independent across source
clauses, so the whole formula is satisfiable iff the source is.

The reduction is linear in the source size (7 clauses, 3 variables per
source clause), hence polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to a 3-SAT instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses: list[list[int]] = []
    next_var = m

    for clause in clauses:
        a, b, c = clause
        x1 = next_var + 1
        x2 = next_var + 2
        x3 = next_var + 3
        next_var += 3

        out_clauses.append([a, b, c])
        out_clauses.append([-a, -b, x1])
        out_clauses.append([-a, -b, -x1])
        out_clauses.append([-a, -c, x2])
        out_clauses.append([-a, -c, -x2])
        out_clauses.append([-b, -c, x3])
        out_clauses.append([-b, -c, -x3])

    return {"num_vars": next_var, "clauses": out_clauses}
