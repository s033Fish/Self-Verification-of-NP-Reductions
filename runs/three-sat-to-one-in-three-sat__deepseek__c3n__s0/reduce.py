"""Polynomial-time reduction from 3-SAT (SOURCE) to 1-in-3-SAT (TARGET).

Idea
----
The target problem only allows positive literals, so every original variable v
gets a positive target variable v.  For each original variable v whose negation
is needed we add a fresh variable nv together with the *complement gadget*

    (v, nv, u0), (v, nv, u1), (u0, u1, u2)

which is satisfiable (over u0,u1,u2) exactly when nv = NOT v.  (Exhaustively
checked: for every x,y in {0,1} the gadget has a satisfying assignment iff
y != x.)

Each 3-SAT clause (l1, l2, l3) is replaced by the *OR gadget*

    (A,  u0, u1)
    (NB, u0, u2)
    (NC, u1, u3)

where A = rep(l1), NB = rep(NOT l2), NC = rep(NOT l3), rep(+v)=v and
rep(-v)=nv, and u0..u3 are fresh.  Because the clause's three variables are
distinct, A, NB, NC are three distinct target variables.  This gadget is
satisfiable (over u0..u3) exactly when A OR B OR C holds, i.e. exactly when
l1 OR l2 OR l3 holds.  (Exhaustively checked for all 8 input combinations.)

Therefore the produced 1-in-3-SAT instance is satisfiable iff the original
3-SAT instance is.  The construction uses O(m + #clauses) variables and
O(m + #clauses) clauses, so it runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Which variables need a "negation" companion variable?
    # rep(+v) = v, rep(-v) = nv.  We use rep(l1), rep(-l2), rep(-l3).
    needed: set[int] = set()
    for clause in clauses:
        l1, l2, l3 = clause
        if l1 < 0:
            needed.add(-l1)
        for lit in (l2, l3):
            neg = -lit
            if neg < 0:
                needed.add(-neg)

    next_id = num_vars + 1

    # Allocate companion (negation) variables.
    neg_var: dict[int, int] = {}
    for v in sorted(needed):
        neg_var[v] = next_id
        next_id += 1

    out_clauses: list[list[int]] = []

    # Complement gadgets: force neg_var[v] == NOT v.
    for v in sorted(needed):
        nv = neg_var[v]
        u0, u1, u2 = next_id, next_id + 1, next_id + 2
        next_id += 3
        out_clauses.append([v, nv, u0])
        out_clauses.append([v, nv, u1])
        out_clauses.append([u0, u1, u2])

    def rep(literal: int) -> int:
        v = abs(literal)
        return v if literal > 0 else neg_var[v]

    # OR gadgets, one per source clause.
    for clause in clauses:
        l1, l2, l3 = clause
        a = rep(l1)
        nb = rep(-l2)
        nc = rep(-l3)
        u0, u1, u2, u3 = next_id, next_id + 1, next_id + 2, next_id + 3
        next_id += 4
        out_clauses.append([a, u0, u1])
        out_clauses.append([nb, u0, u2])
        out_clauses.append([nc, u1, u3])

    return {"num_vars": next_id - 1, "clauses": out_clauses}
