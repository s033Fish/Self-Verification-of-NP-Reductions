"""Polynomial-time reduction from 1-in-3-SAT (SOURCE) to 3-SAT (TARGET).

Idea
----
A source clause (a, b, c) is satisfied iff EXACTLY ONE of a, b, c is true,
which is equivalent to the conjunction

    (a v b v c)  ^  (~a v ~b)  ^  (~a v ~c)  ^  (~b v ~c).

The first clause is already a valid 3-SAT clause.  Each 2-literal clause
(~u v ~v) is replaced, using a fresh auxiliary variable p, by the pair

    (~u v ~v v p)  ^  (~u v ~v v ~p).

For any fixed values of u and v these two clauses are satisfiable iff
(~u v ~v) holds: if u and v are both true the pair demands p and ~p
simultaneously, otherwise p can be chosen to satisfy both.  The auxiliary
variables are free, so they never change satisfiability of the whole
formula.

Each source clause therefore becomes 1 + 3*2 = 7 target clauses and uses 3
fresh variables, so the reduction is polynomial (linear) in the input size.
"""

from __future__ import annotations

from typing import Any

from problems import SOURCE, TARGET


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 1-in-3-SAT instance to an equisatisfiable 3-SAT instance."""
    SOURCE.validate(instance)

    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses: list[list[int]] = []
    next_var = num_vars + 1

    for a, b, c in clauses:
        # At least one of a, b, c is true.
        out_clauses.append([a, b, c])
        # At most one of a, b, c is true: for every pair, not both true.
        for u, v in ((a, b), (a, c), (b, c)):
            p = next_var
            next_var += 1
            out_clauses.append([-u, -v, p])
            out_clauses.append([-u, -v, -p])

    result = {"num_vars": next_var - 1, "clauses": out_clauses}
    TARGET.validate(result)
    return result
