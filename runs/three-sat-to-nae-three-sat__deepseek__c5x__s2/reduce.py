"""Polynomial-time reduction from 3-SAT (SOURCE) to NAE-3-SAT (TARGET).

Gadget identity used:
    NAE(a, b, c, d)  <=>  exists t. NAE(a, b, t) AND NAE(c, d, -t)

Proof sketch:
  * If a,b,c,d are all equal, then NAE(a,b,t) forces t != a while
    NAE(c,d,-t) forces -t != a, i.e. t == a: contradiction, so no t works.
  * Otherwise pick t:
      - if a != b, the first clause is always fine; pick t so that the
        second clause is fine (if c == d choose t = c, else any t).
      - if a == b, then (since not all four are equal) c,d are not both a;
        pick t != a, so -t == a and the second clause is fine.
    In both cases both clauses hold.

Reduction:
  For every source clause (l1 v l2 v l3) introduce a fresh variable t_i and
  use one global fresh variable z.  Add the two NAE-3 clauses
        [l1, l2,  t_i]
        [l3,  z, -t_i]
  which together encode NAE(l1, l2, l3, z).

Correctness:
  (=>) If the 3-SAT formula is satisfiable, set z = False.  Every clause has
       at least one true literal, so NAE(l1,l2,l3,False) holds; by the gadget
       identity a suitable t_i exists for each clause.
  (<=) If the NAE instance is satisfiable, then for each i the pair of clauses
       implies NAE(l1,l2,l3,z).  If z = False this says at least one of
       l1,l2,l3 is true.  If z = True, complement every variable: NAE is
       invariant under complementing all literals, so we get a satisfying
       assignment with z = False, which again makes every clause have a true
       literal.  Hence the original formula is satisfiable.

All new variables are numbered above the source's num_vars, so clauses always
have 3 literals on 3 different variables.  The reduction adds exactly 2
clauses and 1 variable per source clause: polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    z = num_vars + 1          # global fresh variable
    next_var = z + 1          # fresh variable counter

    new_clauses: list[list[int]] = []
    for clause in clauses:
        l1, l2, l3 = clause
        t = next_var
        next_var += 1
        new_clauses.append([l1, l2, t])
        new_clauses.append([l3, z, -t])

    return {"num_vars": next_var - 1, "clauses": new_clauses}
