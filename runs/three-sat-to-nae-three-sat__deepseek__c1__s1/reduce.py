"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Source instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance: {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

Construction
------------
Let the source have m variables and k clauses.  Introduce one fresh global
variable t and, for every source clause i, one fresh variable y_i.  Replace
each source clause (l1 v l2 v l3) by the two NAE clauses

    NAE(l1, l2, y_i)
    NAE(~y_i, l3, t)

Target variable numbering: source variables keep 1..m, t = m+1, and
y_i = m+2+i.

Why it works
------------
Fix a source clause (a v b v c) and its auxiliary y.

* With t = false, NAE(~y, c, false) holds iff y = false or c = true, so
  when c = false it forces y = false.  Then NAE(a, b, y) = NAE(a, b, false)
  holds iff a or b is true.  If c is true the first constraint is vacuous
  and some y always works (take y = a if a != b, else y = ~a).  Hence the
  gadget is satisfiable (over y) exactly when a v b v c holds.

* With t = true, NAE(~y, c, true) holds iff y = true or c = false, so when
  c = true it forces y = true.  Then NAE(a, b, y) = NAE(a, b, true) holds
  iff a or b is false.  If c is false the constraint is vacuous.  So the
  gadget is satisfiable exactly when ~a v ~b v ~c holds.

Consequently, if the target is satisfiable then either t = false and every
source clause is satisfied, or t = true and flipping every source variable
satisfies every source clause.  In both cases the source is satisfiable.
Conversely, any satisfying source assignment extends to a target assignment
by taking t = false and choosing each y_i as above.  So the answers agree.

The construction uses m + 1 + k variables and 2k clauses, so it is linear
(hence polynomial) in the source size and performs no search.
"""


def reduce(instance):
    """Return an equivalent NAE-3-SAT instance for a 3-SAT instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    t = m + 1
    next_var = m + 2
    target_clauses = []

    for clause in clauses:
        l1, l2, l3 = clause
        y = next_var
        next_var += 1
        target_clauses.append([l1, l2, y])
        target_clauses.append([-y, l3, t])

    return {"num_vars": next_var - 1, "clauses": target_clauses}
