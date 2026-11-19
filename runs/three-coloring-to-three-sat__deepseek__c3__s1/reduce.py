"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0,1,2} introduce a boolean
variable x_{v,c} (meaning "vertex v gets colour c").  Variables are numbered
1..3n via  x_{v,c} = 3*v + c + 1.

Clauses:
  * (x_{v,0} v x_{v,1} v x_{v,2})                       at least one colour
  * (~x_{v,c} v ~x_{v,d})  for c < d                    at most one colour
  * (~x_{u,c} v ~x_{v,c})  for every edge (u,v), colour c   endpoints differ

The last two families are 2-literal clauses, while the target requires every
clause to have exactly 3 literals on 3 distinct variables.  A 2-literal
clause (a v b) is replaced by the pair of 3-literal clauses
    (a v b v p) and (a v b v ~p)
for a fresh variable p.  Together these are logically equivalent to (a v b):
if a v b holds, choose p freely; if a v b is false, both clauses are false.

The construction is clearly polynomial: O(n + |edges|) variables and clauses.
"""

from typing import Any, Dict, List


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses: List[List[int]] = []

    def var(v: int, c: int) -> int:
        # x_{v,c} in 1..3n
        return 3 * v + c + 1

    # At least one colour per vertex (already a 3-literal clause).
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Helper: emit a 2-literal clause (a v b), padded with a fresh variable.
    def add_binary(a: int, b: int) -> None:
        nonlocal num_vars
        num_vars += 1
        p = num_vars
        clauses.append([a, b, p])
        clauses.append([a, b, -p])

    # At most one colour per vertex.
    for v in range(n):
        for c in range(3):
            for d in range(c + 1, 3):
                add_binary(-var(v, c), -var(v, d))

    # Adjacent vertices must differ: for each colour they cannot share it.
    for u, w in edges:
        for c in range(3):
            add_binary(-var(u, c), -var(w, c))

    return {"num_vars": num_vars, "clauses": clauses}
