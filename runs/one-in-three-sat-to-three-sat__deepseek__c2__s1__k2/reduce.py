"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source instance (1-in-3-SAT, positive):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
    Yes iff some assignment makes EXACTLY ONE variable true in every clause.

Target instance (3-SAT):
    {"num_vars": m', "clauses": [[l1, l2, l3], ...]}
    Yes iff some assignment makes every clause contain at least one true literal.

Reduction
---------
For each source clause (a, b, c) we must express "exactly one of a, b, c is
true", i.e. "at least one is true" AND "no two are true together".

* At least one: the 3-literal clause [a, b, c] (already a valid target clause).

* At most one: for every pair {x, y} among {a, b, c} we need (not x or not y).
  A 2-literal clause is not allowed in the target, so we pad it with a fresh
  variable p and emit the two 3-literal clauses

        [-x, -y,  p]
        [-x, -y, -p]

  which together are equivalent to (not x or not y): if both x and y are true
  the two clauses force p and not p (unsatisfiable); otherwise both clauses are
  already satisfied.  Each pair gets its own fresh variable, so the padding
  variables never interfere with anything else.

The fresh variables are numbered m+1, m+2, ... .  Each source clause creates
exactly 3 fresh variables and 7 target clauses, so the reduction is linear
(polynomial) in the input size.  A source formula with no clauses maps to a
target formula with no clauses, which is satisfiable for any num_vars.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    new_clauses = []
    next_var = num_vars

    for a, b, c in clauses:
        # At least one of a, b, c is true.
        new_clauses.append([a, b, c])

        # At most one of a, b, c is true: pairwise negative clauses, padded
        # to length 3 with a fresh variable.
        for x, y in ((a, b), (a, c), (b, c)):
            next_var += 1
            p = next_var
            new_clauses.append([-x, -y, p])
            new_clauses.append([-x, -y, -p])

    return {"num_vars": next_var, "clauses": new_clauses}
