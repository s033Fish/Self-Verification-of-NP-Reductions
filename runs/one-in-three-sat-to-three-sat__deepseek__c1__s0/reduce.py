"""Polynomial-time reduction from 1-in-3-SAT (positive) to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[a, b, c], ...]} where each
clause lists three distinct positive variables and is satisfied iff exactly
one of a, b, c is true.

Target instance: {"num_vars": M, "clauses": [[l1, l2, l3], ...]} where each
clause has three literals on three distinct variables and is satisfied iff at
least one literal is true.

Construction
------------
For every source clause (a, b, c) we introduce one fresh auxiliary variable x
and emit seven target clauses:

    (a  v  b  v  c)              -- at least one of a, b, c is true
    (~a v ~b v  x), (~a v ~b v ~x)   -- forbids a and b both true
    (~a v ~c v  x), (~a v ~c v ~x)   -- forbids a and c both true
    (~b v ~c v  x), (~b v ~c v ~x)   -- forbids b and c both true

Each pair of padded clauses is satisfiable iff the corresponding 2-literal
clause (~p v ~q) holds: if p and q are both true they demand x and ~x at once,
otherwise x can be set to satisfy both.  Hence the seven clauses together are
satisfiable iff exactly one of a, b, c is true.  The fresh variable x is local
to its clause, so the whole target formula is satisfiable iff the source
formula is.

The reduction is linear: one new variable and seven new clauses per source
clause, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a positive 1-in-3-SAT instance to a 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    new_clauses = []
    next_var = num_vars

    for a, b, c in clauses:
        next_var += 1
        x = next_var
        # At least one of the three variables is true.
        new_clauses.append([a, b, c])
        # At most one of the three variables is true, pair by pair.
        for p, q in ((a, b), (a, c), (b, c)):
            new_clauses.append([-p, -q, x])
            new_clauses.append([-p, -q, -x])

    return {"num_vars": next_var, "clauses": new_clauses}
