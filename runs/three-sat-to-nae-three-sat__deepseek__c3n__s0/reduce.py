"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Given a 3-SAT instance with variables 1..n and clauses C_1..C_m, we build a
NAE-3-SAT instance as follows.

Introduce a fresh global variable y = n + 1, and for each clause C_i a fresh
auxiliary variable z_i = n + 1 + i.

For a clause C_i = (a v b v c) (a, b, c literals over the original variables),
add the two NAE-3 clauses

    NAE(a, b, z_i)
    NAE(-z_i, c, y)

Correctness
-----------
NAE-3-SAT is invariant under complementing a whole assignment (flipping every
variable keeps "not all equal" true).  Hence a NAE formula is satisfiable iff
it has a satisfying assignment with y = false.  Under y = false the pair of
clauses above is satisfiable (for the fresh z_i) exactly when at least one of
a, b, c is true:

  * If at least one of a, b, c is true, then NAE(a, b, c, false) holds (the
    four values are not all equal).  The 4-literal NAE is equivalent to the
    two 3-literal clauses via z_i, so they are satisfiable.
  * If a = b = c = false, then NAE(a, b, z_i) forces z_i = true, while
    NAE(-z_i, false, false) forces z_i = false -- a contradiction.

The 4-literal equivalence NAE(a,b,c,d) <=> exists z: NAE(a,b,z) and
NAE(-z,c,d) is checked directly: if a != b pick any z with the second clause
satisfied; if a == b, at least one of c, d differs from a, so z = -a works.
Conversely, if a=b=c=d then the first clause needs z != a and the second
needs -z != a, i.e. z = a, a contradiction.

Thus the constructed NAE-3-SAT instance is satisfiable iff the original 3-SAT
instance is.  The construction is linear in the input size.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    y = num_vars + 1
    target_clauses: list[list[int]] = []

    for index, clause in enumerate(clauses):
        a, b, c = clause
        z = y + 1 + index
        target_clauses.append([a, b, z])
        target_clauses.append([-z, c, y])

    return {"num_vars": y + len(clauses), "clauses": target_clauses}
