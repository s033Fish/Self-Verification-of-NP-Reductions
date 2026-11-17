"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source instance (1-in-3-SAT):
    {"num_vars": m, "clauses": [[a, b, c], ...]}   (positive literals only)

Target instance (3-SAT):
    {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

Reduction idea
--------------
A 1-in-3 clause (a, b, c) means: at least one of a, b, c is true AND no two
of them are true together.  In 3-SAT:

    at least one   ->  (a v b v c)
    no two true    ->  (~a v ~b), (~a v ~c), (~b v ~c)

Each 2-literal clause (l1 v l2) is turned into two 3-literal clauses using a
single fresh variable p:

    (l1 v l2 v p)  and  (l1 v l2 v ~p)

Together these are equivalent to (l1 v l2): whatever value p takes, one of
the two clauses forces l1 v l2.  Since p is fresh it never clashes with the
original variables, so every produced clause has 3 literals on 3 distinct
variables.  The whole construction is linear in the number of clauses.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to an equisatisfiable 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    if not clauses:
        # No clauses: already a valid 3-SAT instance and it is satisfiable.
        return {"num_vars": num_vars, "clauses": []}

    # One fresh padding variable, strictly larger than every source variable.
    pad = num_vars + 1
    out_clauses: list[list[int]] = []

    for a, b, c in clauses:
        # At least one of a, b, c is true.
        out_clauses.append([a, b, c])
        # No two of a, b, c are true together; pad each pair to length 3.
        for x, y in ((a, b), (a, c), (b, c)):
            out_clauses.append([-x, -y, pad])
            out_clauses.append([-x, -y, -pad])

    return {"num_vars": pad, "clauses": out_clauses}
