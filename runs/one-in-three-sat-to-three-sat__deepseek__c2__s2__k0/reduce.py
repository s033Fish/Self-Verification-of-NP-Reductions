"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source instance (1-in-3-SAT):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where each clause contains three distinct positive variables and is
satisfied iff exactly one of a, b, c is true.

Target instance (3-SAT):
    {"num_vars": m', "clauses": [[l1, l2, l3], ...]}
where each clause contains three literals on three distinct variables and
is satisfied iff at least one literal is true.

Reduction:
    For every source clause (a, b, c) introduce one fresh variable p and
    emit the following 3-SAT clauses:

        ( a  v  b  v  c)          # at least one of a, b, c is true
        (~a  v ~b  v  p)
        (~a  v ~b  v ~p)          # together: ~a v ~b
        (~a  v ~c  v  p)
        (~a  v ~c  v ~p)          # together: ~a v ~c
        (~b  v ~c  v  p)
        (~b  v ~c  v ~p)          # together: ~b v ~c

    The pairs of clauses containing p and ~p are equivalent to the
    2-clauses (~a v ~b), (~a v ~c), (~b v ~c), i.e. at most one of
    a, b, c is true.  Combined with the first clause this is exactly
    "exactly one of a, b, c is true".

The fresh variable p is local to its source clause and is otherwise
unconstrained, so the reduction is sound and complete.  It runs in
O(number of source clauses) time and adds one variable and six clauses
per source clause.
"""


def reduce(instance):
    """Return a 3-SAT instance equivalent to the given 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses = []
    next_var = num_vars

    for a, b, c in clauses:
        # At least one of a, b, c is true.
        out_clauses.append([a, b, c])

        # Fresh variable used to pad the three "at most one" 2-clauses.
        next_var += 1
        p = next_var

        # At most one of a, b, c is true, expressed as pairwise clauses.
        out_clauses.append([-a, -b, p])
        out_clauses.append([-a, -b, -p])
        out_clauses.append([-a, -c, p])
        out_clauses.append([-a, -c, -p])
        out_clauses.append([-b, -c, p])
        out_clauses.append([-b, -c, -p])

    return {"num_vars": next_var, "clauses": out_clauses}
