"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

Source instance (1-in-3-SAT): {"num_vars": m, "clauses": [[a, b, c], ...]}
with positive, pairwise-distinct variables per clause.  A clause is satisfied
when EXACTLY ONE of a, b, c is true.

Target instance (3-SAT): {"num_vars": M, "clauses": [[l1, l2, l3], ...]} with
literals over variables 1..M; a clause is satisfied when AT LEAST ONE literal
is true.

Encoding
--------
For a source clause (a, b, c), "exactly one is true" is the conjunction of

    (a or b or c)                       # at least one true
    (not a or not b)                    # at most one true
    (not a or not c)
    (not b or not c)

The ternary clause is already a valid 3-SAT clause.  Each binary clause
(not u or not v) is replaced, using a fresh variable t, by the pair

    (not u or not v or  t)
    (not u or not v or not t)

which is equivalent to (not u or not v): if the binary clause holds both new
clauses hold for either value of t; if it fails (u = v = true) then the two
new clauses demand t and not t simultaneously, so they are unsatisfiable.
Each fresh t is used only by its own pair, so the auxiliary variables are
independent and can always be chosen to satisfy the padding when the binary
clause holds.

Hence the target formula is satisfiable iff every source clause has exactly
one true variable, i.e. iff the source instance is a yes-instance.  The
reduction adds 3 fresh variables and 6 extra clauses per source clause, so it
runs in linear (certainly polynomial) time.
"""


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to an equisatisfiable 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses = []
    next_var = num_vars + 1

    for a, b, c in clauses:
        # At least one of the three is true.
        out_clauses.append([a, b, c])

        # At most one is true: pad each binary clause with a fresh variable.
        for u, v in ((a, b), (a, c), (b, c)):
            t = next_var
            next_var += 1
            out_clauses.append([-u, -v, t])
            out_clauses.append([-u, -v, -t])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
