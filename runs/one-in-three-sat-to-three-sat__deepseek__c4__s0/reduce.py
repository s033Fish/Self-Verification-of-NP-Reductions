"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source (OneInThreeSat): {"num_vars": m, "clauses": [[a, b, c], ...]}
  Each clause must have EXACTLY ONE of its three (positive) variables true.

Target (ThreeSat): {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
  Each clause must have AT LEAST ONE true literal.

Reduction
---------
For a source clause (a, b, c), "exactly one true" is equivalent to

    at-least-one:  (a v b v c)
    at-most-one:   (not a v not b) & (not a v not c) & (not b v not c)

The at-least-one clause is already a valid 3-clause.  Each at-most-one
clause is a 2-clause; we turn a 2-clause (L1 v L2) into the pair

    (L1 v L2 v z) & (L1 v L2 v not z)

which is equivalent to (L1 v L2) for a fresh variable z (if L1 v L2 is
false, z would have to be both true and false).  A single fresh variable
z = m + 1 is shared by every padded clause; it is distinct from all source
variables, so every produced clause uses three different variables.

The reduction emits a constant number of clauses per source clause, hence
runs in polynomial time and uses no solvers.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to an equisatisfiable 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    if not clauses:
        # No clauses is a yes-instance for any m (including m = 0).
        return {"num_vars": num_vars, "clauses": []}

    z = num_vars + 1  # fresh padding variable, distinct from 1..num_vars

    out: list[list[int]] = []
    for clause in clauses:
        a, b, c = clause

        # At least one of a, b, c is true.
        out.append([a, b, c])

        # At most one of a, b, c is true: no pair may both be true.
        for u, v in ((a, b), (a, c), (b, c)):
            # (not u v not v) padded with the fresh variable z.
            out.append([-u, -v, z])
            out.append([-u, -v, -z])

    return {"num_vars": z, "clauses": out}
