"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Construction
------------
Let the source formula have variables 1..m and clauses C_j = (l1 v l2 v l3).

Introduce one global variable z = m+1, and one fresh auxiliary variable
y_j = m+2+j for every source clause C_j.

For each source clause C_j = [l1, l2, l3], emit the two NAE-3 clauses

    [l1, l2, y_j]        and        [l3, z, -y_j].

Correctness
-----------
The 4-literal NAE constraint NAE(a,b,c,d) is equivalent to

    exists y . NAE(a,b,y) and NAE(c,d,-y),

because:
  * If a,b,c,d are all equal to v, the first clause forces y = -v, and then
    the second clause becomes NAE(v,v,v), which is false.
  * If they are not all equal, a suitable y exists (if a != b any y works
    when c != d, and y can be chosen otherwise; symmetrically when a = b).

Thus, existentially eliminating each local y_j, the constructed formula is
satisfiable iff there is an assignment to the original variables and z with

    NAE(l1, l2, l3, z)  for every source clause.

If z is false this says exactly that every source clause has a true literal,
i.e. the source formula is satisfiable.  If z is true it says that every
source clause has a false literal; complementing the assignment then makes
every source clause have a true literal, so again the source is satisfiable.
Conversely any satisfying assignment of the source, with z set to false,
satisfies the constructed NAE formula.  Hence the two answers coincide.

The construction is linear in the size of the input.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an equisatisfiable NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    z = num_vars + 1
    new_clauses = []

    for index, clause in enumerate(clauses):
        l1, l2, l3 = clause
        y = num_vars + 2 + index
        # NAE(l1, l2, l3, z) encoded with the fresh variable y.
        new_clauses.append([l1, l2, y])
        new_clauses.append([l3, z, -y])

    return {
        "num_vars": num_vars + 1 + len(clauses),
        "clauses": new_clauses,
    }
