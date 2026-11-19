"""Polynomial-time reduction from 1-in-3-SAT (SOURCE) to 3-SAT (TARGET).

SOURCE instance: {"num_vars": m, "clauses": [[a, b, c], ...]} where each
clause has 3 distinct positive variables, and it is a yes-instance iff some
assignment makes EXACTLY ONE variable in every clause true.

TARGET instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]} with literals
+/-v on 3 distinct variables, yes iff every clause has at least one true
literal.

Reduction idea
--------------
"Exactly one of a, b, c is true" is equivalent to the conjunction of:

    (a v b v c)                      at least one is true
    (not a v not b)                  at most one of a, b is true
    (not a v not c)                  at most one of a, c is true
    (not b v not c)                  at most one of b, c is true

The first clause is already a 3-clause.  Each 2-clause (not x v not y) is
turned into two 3-clauses using a fresh auxiliary variable z:

    (not x v not y v z) and (not x v not y v not z)

This pair is satisfiable (for some value of z) exactly when (not x v not y)
is satisfiable: if (not x v not y) holds both clauses are satisfied whatever
z is; if it fails then both clauses force z true and z false, impossible.

We use one fresh variable per pair so every produced clause has 3 distinct
variables.  The construction uses O(#clauses) new variables and clauses, so
it runs in polynomial time.  The auxiliary variables are free in the target;
the projection of any satisfying assignment onto the original variables
satisfies the 1-in-3 conditions, and conversely any 1-in-3 assignment extends
to a satisfying assignment by setting the auxiliary variables arbitrarily.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to a 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses: list[list[int]] = []
    next_var = num_vars  # fresh variables are num_vars+1, num_vars+2, ...

    for clause in clauses:
        a, b, c = clause

        # At least one of a, b, c is true.
        out_clauses.append([a, b, c])

        # At most one of each pair is true, padded to 3-clauses with a fresh
        # auxiliary variable.
        for x, y in ((a, b), (a, c), (b, c)):
            next_var += 1
            z = next_var
            out_clauses.append([-x, -y, z])
            out_clauses.append([-x, -y, -z])

    return {"num_vars": next_var, "clauses": out_clauses}
