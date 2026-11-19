"""Polynomial-time reduction from 3-Coloring to 3-SAT.

SOURCE (ThreeColoring): {"n": n, "edges": [[u, v], ...]}
TARGET (ThreeSat):      {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} we create a boolean
variable x_{v,c} = 3*v + c + 1, meaning "vertex v receives colour c".

* For each vertex v we add the clause
      (x_{v,0} v x_{v,1} v x_{v,2})
  which says v gets at least one colour.

* For each edge (u, w) and each colour c we must forbid both endpoints
  getting colour c, i.e. add the 2-literal clause
      (~x_{u,c} v ~x_{w,c}).
  Since 3-SAT clauses need exactly 3 literals on 3 distinct variables, we
  introduce one extra variable z = 3*n + 1 and replace each such 2-clause A
  by the pair
      (A v z) and (A v ~z).
  For a fixed z, (A v z) & (A v ~z) is logically equivalent to A, because
  z is either true or false.  All padded clauses share the same z, which is
  fine.

Correctness
-----------
* If G is 3-colourable, set x_{v,c} true iff v has colour c and set z
  arbitrarily; every clause is satisfied.

* If the formula is satisfiable, let S_v = {c : x_{v,c} true}.  Each S_v is
  non-empty (vertex clauses) and for every edge (u,w), S_u and S_w are
  disjoint (edge clauses).  Picking any colour from each S_v yields a proper
  3-colouring, since adjacent vertices have disjoint colour sets.

The construction uses O(n + |E|) variables and clauses, hence runs in
polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-Coloring instance to a 3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    def var(v: int, c: int) -> int:
        return 3 * v + c + 1

    # One padding variable, used to lift 2-literal edge clauses to 3 literals.
    z = 3 * n + 1
    num_vars = 3 * n + 1

    clauses: list[list[int]] = []

    # At least one colour per vertex.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Adjacent vertices must not share a colour.
    for edge in edges:
        u, w = edge
        for c in range(3):
            a = -var(u, c)
            b = -var(w, c)
            clauses.append([a, b, z])
            clauses.append([a, b, -z])

    return {"num_vars": num_vars, "clauses": clauses}
