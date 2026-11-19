"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source instance (positive one-in-three):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where each clause contains exactly three distinct positive variables and is
satisfied iff exactly one of a, b, c is true.

Target instance (3-SAT):
    {"num_vars": m', "clauses": [[l1, l2, l3], ...]}
where each clause contains three literals on three distinct variables and is
satisfied iff at least one literal is true.

Reduction
---------
For every source clause (a, b, c) we add one fresh auxiliary variable x and
the following seven target clauses:

    (a  v  b  v  c)          at least one of a, b, c is true
    (~a v ~b v  x)           forbid a and b together
    (~a v ~b v ~x)
    (~a v ~c v  x)           forbid a and c together
    (~a v ~c v ~x)
    (~b v ~c v  x)           forbid b and c together
    (~b v ~c v ~x)

For a fixed assignment to a, b, c the pair of clauses for a pair (u, v) is
equivalent to (~u v ~v): if u and v are not both true the pair is satisfied
regardless of x, while if both are true one clause forces x true and the
other forces x false, so no value of x works.  Hence the seven clauses are
satisfiable (for some x) exactly when exactly one of a, b, c is true.

Auxiliary variables are numbered m+1, m+2, ...; the resulting formula uses
m + K variables where K is the number of source clauses, and 7K clauses.
"""


def reduce(instance):
    """Return a 3-SAT instance equivalent to the given 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses = []
    next_var = num_vars + 1

    for a, b, c in clauses:
        # At least one of the three variables must be true.
        out_clauses.append([a, b, c])

        # One fresh auxiliary variable per source clause.
        x = next_var
        next_var += 1

        # At most one of the three variables may be true.  Each pairwise
        # constraint (~u v ~v) is padded with x and ~x; together the two
        # clauses are equivalent to the two-literal constraint.
        out_clauses.append([-a, -b, x])
        out_clauses.append([-a, -b, -x])
        out_clauses.append([-a, -c, x])
        out_clauses.append([-a, -c, -x])
        out_clauses.append([-b, -c, x])
        out_clauses.append([-b, -c, -x])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
