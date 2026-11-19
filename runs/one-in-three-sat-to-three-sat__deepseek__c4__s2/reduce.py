"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

SOURCE: OneInThreeSat (positive 1-in-3-SAT)
TARGET: ThreeSat (3-SAT)

Idea
----
For each source clause (a, b, c) we need "exactly one of a, b, c is true",
which is the conjunction of:

  * at least one:  (a v b v c)                      -- already a 3-clause
  * at most one:   (~a v ~b), (~b v ~c), (~a v ~c)  -- 2-clauses

3-SAT requires every clause to have exactly 3 literals on 3 distinct
variables.  A 2-clause (l1 v l2) is replaced by the two 3-clauses

      (l1 v l2 v x)   and   (l1 v l2 v ~x)

with x a fresh variable.  If l1 v l2 is false both clauses force x and ~x,
which is impossible; otherwise both clauses are satisfied whatever x is.
Thus the pair is equivalent to (l1 v l2), existentially quantified over x.

All auxiliary variables are fresh (indices m+1, m+2, ...), so the target
formula is satisfiable iff the source formula is.  The construction adds a
constant number of clauses/variables per source clause and runs in
polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to a 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    target_clauses = []
    next_var = num_vars

    def fresh():
        nonlocal next_var
        next_var += 1
        return next_var

    for clause in clauses:
        a, b, c = clause

        # at least one of a, b, c is true
        target_clauses.append([a, b, c])

        # at most one of a, b, c is true: pairwise 2-clauses, padded to 3
        for u, v in ((a, b), (b, c), (a, c)):
            x = fresh()
            target_clauses.append([-u, -v, x])
            target_clauses.append([-u, -v, -x])

    return {"num_vars": next_var, "clauses": target_clauses}
