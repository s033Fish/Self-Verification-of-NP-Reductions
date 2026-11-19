"""Polynomial-time reduction from 3-SAT (SOURCE) to NAE-3-SAT (TARGET).

Construction
------------
Let the 3-SAT instance have variables 1..m and clauses C_i = (l1 v l2 v l3).

If there are no clauses, the instance is a yes-instance and we simply return
an empty NAE-3-SAT formula (also a yes-instance for any m).

Otherwise add one global variable x = m+1 and, for every clause i, one fresh
variable y_i = m+2+i.  Replace each clause C_i by the two NAE clauses

    NAE(l1, l2, y_i)
    NAE(-y_i, l3, x)

Claim: the resulting NAE-3-SAT formula is satisfiable iff the original 3-SAT
formula is.

* If x is set to false, the second clause is violated exactly when y_i is true
  and l3 is false, i.e. it forces y_i -> l3.  The first clause is violated
  exactly when l1 = l2 = y_i.  The pair is satisfiable for some y_i iff at
  least one of l1, l2, l3 is true (if all are false the second forces y_i false
  and the first becomes all-false; conversely an explicit y_i can be chosen).
  So with x = false the formula is satisfiable iff the 3-SAT instance is.

* NAE clauses are invariant under complementing every variable.  Hence any
  satisfying assignment with x = true can be complemented into one with
  x = false (over the same original variables complemented), which by the
  previous point yields a satisfying assignment of the 3-SAT instance.

The construction is linear in the input size, hence polynomial time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    if not clauses:
        return {"num_vars": num_vars, "clauses": []}

    x = num_vars + 1
    new_clauses = []
    for i, (l1, l2, l3) in enumerate(clauses):
        y = num_vars + 2 + i
        new_clauses.append([l1, l2, y])
        new_clauses.append([-y, l3, x])

    return {"num_vars": num_vars + 1 + len(clauses), "clauses": new_clauses}
