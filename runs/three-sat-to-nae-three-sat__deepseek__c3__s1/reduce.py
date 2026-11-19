"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Given a 3-SAT instance with variables 1..m and clauses (l1 v l2 v l3):

  * Introduce one global variable z = m+1.
  * For each clause i, introduce a fresh auxiliary variable y_i.
  * Replace the clause by the two NAE-3 clauses
        (l1, l2, y_i)   and   (-y_i, l3, z).

Why this works
--------------
NAE(l1, l2, l3, z) is equivalent to the existence of a y with
NAE(l1, l2, y) and NAE(-y, l3, z) (a standard 4-to-3 NAE split):
  - If l1 != l2, take y = l3 when l3 == z, else any y.
  - If l1 == l2 == c, take y = -c (one of l3, z differs from c).
  - Conversely, if all of l1,l2,l3,z were equal to c, then
    NAE(l1,l2,y) forces y = -c, making (-y,l3,z) = (c,c,c), a
    contradiction.

NAE-SAT is invariant under complementing every variable, so a satisfying
assignment can be complemented to one with z = false.  With z = false,
NAE(l1, l2, l3, z) holds iff not all of l1,l2,l3 are false, i.e. iff the
original clause (l1 v l2 v l3) is satisfied.  Hence the NAE instance is
satisfiable iff the 3-SAT instance is.

The construction uses O(m + k) variables and 2k clauses for k source
clauses, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # No clauses: already satisfiable (yes) in both problems.
    if not clauses:
        return {"num_vars": num_vars, "clauses": []}

    z = num_vars + 1
    new_clauses = []
    next_var = num_vars + 1
    for clause in clauses:
        next_var += 1
        y = next_var
        l1, l2, l3 = clause
        new_clauses.append([l1, l2, y])
        new_clauses.append([-y, l3, z])

    return {"num_vars": next_var, "clauses": new_clauses}
