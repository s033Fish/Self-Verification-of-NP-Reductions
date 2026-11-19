"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Idea
----
For literals a, b, c, d the 4-literal not-all-equal constraint is equivalent to

    NAE(a, b, c, d)  <=>  exists y: NAE(a, b, y) AND NAE(c, d, -y)

(If a=b=c=d then the two clauses force y and -y to both be the "different"
value, a contradiction; otherwise a suitable y always exists.)

We use this with a single global variable ``g`` shared by every clause.  For a
3-SAT clause (l1 or l2 or l3) we add a fresh variable y_i and the two NAE-3
clauses

    NAE(l1, l2, y_i)
    NAE(l3, g, -y_i)

which together are satisfiable exactly when NAE(l1, l2, l3, g) holds.

* With g = 0 this is "not all of l1,l2,l3,0 equal" = l1 or l2 or l3.
* With g = 1 this is "not all of l1,l2,l3,1 equal" = not l1 or not l2 or not l3,
  i.e. the complemented clause.

So the constructed formula is satisfiable iff the original 3-CNF is satisfiable
for g = 0, or its complement is satisfiable for g = 1.  A CNF is satisfiable
iff its complement is (complement every variable of a satisfying assignment),
hence the reduction is correct.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    k = len(clauses)

    # No clauses: already a yes-instance of NAE-3-SAT (for any num_vars).
    if k == 0:
        return {"num_vars": num_vars, "clauses": []}

    # Global selector variable g, plus one fresh y_i per clause.
    g = num_vars + 1
    new_clauses = []
    for i, clause in enumerate(clauses):
        l1, l2, l3 = clause
        y = num_vars + 2 + i
        new_clauses.append([l1, l2, y])
        new_clauses.append([l3, g, -y])

    return {"num_vars": num_vars + 1 + k, "clauses": new_clauses}
