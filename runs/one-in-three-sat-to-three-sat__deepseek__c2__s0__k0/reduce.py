"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[a, b, c], ...]} where each
clause lists three different positive variables and is satisfied iff
exactly one of them is true.

Target instance: {"num_vars": m', "clauses": [[l1, l2, l3], ...]} where
each clause has three literals on three different variables and is
satisfied iff at least one literal is true.

Construction
------------
A 1-in-3 clause (a, b, c) is equivalent to the CNF

    (a v b v c)  /\  (~a v ~b)  /\  (~a v ~c)  /\  (~b v ~c)

The first conjunct is already a valid 3-SAT clause.  Each 2-literal
clause (p v q) is turned into two 3-literal clauses

    (p v q v x)  /\  (p v q v ~x)

using a fresh variable x.  For any assignment of the original variables,
these two clauses are simultaneously satisfiable iff (p v q) is true:
if p v q holds, choose x arbitrarily; if p v q is false, the two clauses
demand x and ~x, a contradiction.  The same fresh variable can be shared
by every 2-literal clause, since the equivalence holds pair by pair.

The result uses at most one extra variable and at most 4 clauses per
source clause, so the reduction runs in linear (hence polynomial) time.
"""


def reduce(instance):
    """Return a 3-SAT instance yes iff the 1-in-3-SAT input is yes."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # No clauses: both problems accept, keep the same variable count.
    if not clauses:
        return {"num_vars": num_vars, "clauses": []}

    # One fresh variable shared by all expanded 2-literal clauses.
    fresh = num_vars + 1

    out_clauses = []
    for a, b, c in clauses:
        # "at least one of a, b, c is true"
        out_clauses.append([a, b, c])
        # "no two of a, b, c are true", each 2-clause expanded to 3 literals.
        for u, v in ((a, b), (a, c), (b, c)):
            out_clauses.append([-u, -v, fresh])
            out_clauses.append([-u, -v, -fresh])

    return {"num_vars": num_vars + 1, "clauses": out_clauses}
