"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

SOURCE: OneInThreeSat  {"num_vars": m, "clauses": [[a, b, c], ...]}
TARGET: ThreeSat       {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

A source clause (a, b, c) demands EXACTLY ONE of a, b, c be true, i.e.
  (at least one true) AND (at most one true).

  * at least one true : (a v b v c)          -- already a 3-clause
  * at most one true  : pairwise (not u v not v) for each pair {u, v}

A 2-clause (not u v not v) is not allowed in the target, so it is padded
with a fresh variable x into two 3-clauses:

    (not u v not v v x)  and  (not u v not v v not x)

For any fixed values of u and v these two clauses are simultaneously
satisfiable iff (not u v not v) holds (choose x true / false accordingly),
and x is fresh so it never interferes with anything else.

Hence the constructed 3-SAT formula is satisfiable iff the original
1-in-3-SAT formula is satisfiable.  The construction adds 3 fresh
variables and 6 clauses per source clause, so it runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    """Return a 3-SAT instance equivalent to the 1-in-3-SAT ``instance``."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses = []
    next_var = num_vars + 1

    for a, b, c in clauses:
        # At least one of a, b, c is true.
        out_clauses.append([a, b, c])
        # At most one of a, b, c is true: forbid each pair being true.
        for u, v in ((a, b), (a, c), (b, c)):
            x = next_var
            next_var += 1
            # (not u v not v) padded to two 3-clauses with fresh x.
            out_clauses.append([-u, -v, x])
            out_clauses.append([-u, -v, -x])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
