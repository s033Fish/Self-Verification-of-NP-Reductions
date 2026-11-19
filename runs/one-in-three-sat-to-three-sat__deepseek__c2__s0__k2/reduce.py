"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source instance (1-in-3-SAT):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where every clause has three distinct positive variables and is satisfied
iff exactly one of a, b, c is true.

Target instance (3-SAT):
    {"num_vars": M, "clauses": [[l1, l2, l3], ...]}
where every clause has three literals on three distinct variables and is
satisfied iff at least one literal is true.

Construction
------------
For each source clause (a, b, c) we add:

    (a  v  b  v  c)                       -- at least one of a, b, c is true

and, for each of the three pairs {u, v} from {a, b, c}, we add two clauses
using a fresh auxiliary variable x:

    (~u v ~v v  x)
    (~u v ~v v ~x)

Together these two clauses are equivalent to (~u v ~v), i.e. "not both u
and v are true", because if u and v were both true then x would have to be
both true and false.  The three pairs therefore enforce "at most one of
a, b, c is true".  Combined with the first clause this is exactly
"exactly one of a, b, c is true".

Each source clause uses 3 fresh auxiliary variables, so the reduction is
linear in the size of the input (polynomial time).  Original variables
keep their numbering 1..m; auxiliary variables are numbered m+1, m+2, ...
"""


def reduce(instance):
    """Return a 3-SAT instance equivalent to the given 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses = []
    next_var = num_vars + 1

    for clause in clauses:
        a, b, c = clause

        # At least one of the three is true.
        out_clauses.append([a, b, c])

        # At most one of the three is true: forbid each pair being true
        # together, padding the 2-literal constraint to 3 literals with a
        # fresh variable x via (not u or not v or x) and (not u or not v or not x).
        for u, v in ((a, b), (a, c), (b, c)):
            x = next_var
            next_var += 1
            out_clauses.append([-u, -v, x])
            out_clauses.append([-u, -v, -x])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
