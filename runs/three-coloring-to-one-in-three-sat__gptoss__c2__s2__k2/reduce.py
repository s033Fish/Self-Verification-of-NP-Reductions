"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem (ThreeColoring) expects an instance of the form
```
{"n": n, "edges": [[u, v], ...]}
```
where vertices are numbered 0..n-1.

The target problem (OneInThreeSat) expects an instance of the form
```
{"num_vars": m, "clauses": [[a, b, c], ...]}
```
with variables numbered 1..m and each clause containing three *distinct*
positive integers.  A clause is satisfied iff exactly one of its three
variables is assigned True.

The classic polynomial‑time reduction works as follows:

* For each vertex `v` we introduce three Boolean variables
  `v_R`, `v_G`, `v_B` (representing the three colours).  A clause
  ``[v_R, v_G, v_B]`` forces exactly one of them to be true, i.e. each
  vertex receives exactly one colour.

* For each edge `{u, v}` and each colour `c` we must forbid the two
  endpoints from receiving the same colour.  We introduce a fresh
  auxiliary variable `x_{u,v,c}` and add the clause
  ``[u_c, v_c, x_{u,v,c}]``.  Because the clause must have exactly one
  true literal, `u_c` and `v_c` cannot both be true simultaneously –
  otherwise the clause would contain at least two true literals.
  If both are false, the auxiliary variable simply takes the true value,
  which is harmless.

The construction uses:
    * 3 *n* variables for the vertex colours,
    * 3 *|E| auxiliary variables (one per colour per edge).

Both the number of variables and the number of clauses are linear in the
size of the input graph, so the reduction runs in polynomial time.

The function ``reduce`` below implements this transformation and returns
the target instance in the required dictionary format.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a OneInThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and
        ``"edges"`` (list of ``[u, v]`` pairs).  Vertices are 0‑based.

    Returns
    -------
    dict
        A OneInThreeSat instance with keys ``"num_vars"`` and
        ``"clauses"``.
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    clauses: List[List[int]] = []

    # Helper to map a vertex and a colour (0,1,2) to a variable number.
    # Variables are 1‑based as required by the target format.
    def var_vertex_color(v: int, color: int) -> int:
        return 3 * v + color + 1  # +1 because variables start at 1

    # 1. Vertex colour selection clauses: exactly one colour per vertex.
    for v in range(n):
        clause = [var_vertex_color(v, 0), var_vertex_color(v, 1), var_vertex_color(v, 2)]
        clauses.append(clause)

    # 2. Edge colour inequality clauses using fresh auxiliary variables.
    # We will assign auxiliary variables sequentially after the vertex ones.
    next_aux = 3 * n + 1  # first auxiliary variable index (1‑based)
    for (u, v) in edges:
        for color in range(3):
            aux_var = next_aux
            next_aux += 1
            clause = [var_vertex_color(u, color), var_vertex_color(v, color), aux_var]
            clauses.append(clause)

    num_vars = next_aux - 1  # because next_aux points to the next unused index

    return {"num_vars": num_vars, "clauses": clauses}

