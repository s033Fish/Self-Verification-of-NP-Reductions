"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[a, b, c], ...]} with positive
literals only; a clause is satisfied iff EXACTLY ONE of a, b, c is true.

Target instance: {"num_vars": m', "clauses": [[l1, l2, l3], ...]} where each
clause must contain at least one true literal.

Reduction idea
--------------
For every source clause (a, b, c) we must enforce:
    at least one true  ->  (a v b v c)
    at most one true   ->  (~a v ~b) & (~a v ~c) & (~b v ~c)

The target requires exactly 3 literals on 3 *different* variables, so each
2-literal clause (~u v ~v) is encoded with one fresh variable t:
    (~u v ~v v t) & (~u v ~v v -t)
Both clauses together are satisfiable iff (~u v ~v) holds, and the fresh
variable is distinct from everything else, so each target clause has three
different variables.

Original variables keep their numbers 1..m; fresh variables are numbered
m+1, m+2, ...  A source instance with no clauses maps to a target instance
with no clauses (and the same num_vars), which is satisfiable.
"""

from __future__ import annotations


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = m
    out_clauses = []

    for clause in clauses:
        a, b, c = clause
        # At least one of a, b, c is true.
        out_clauses.append([a, b, c])
        # At most one of a, b, c is true, via the three pairwise
        # "not both" constraints, each padded to 3 literals with a fresh var.
        for u, v in ((a, b), (a, c), (b, c)):
            next_var += 1
            t = next_var
            out_clauses.append([-u, -v, t])
            out_clauses.append([-u, -v, -t])

    return {"num_vars": next_var, "clauses": out_clauses}
