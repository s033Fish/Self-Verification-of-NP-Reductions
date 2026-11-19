"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem is defined in ``problems.py`` as ``ThreeColoring`` with
instances of the form ``{"n": n, "edges": [[u, v], ...]}``.  The target problem
is ``OneInThreeSat`` with instances ``{"num_vars": m, "clauses": [[a, b, c],
...}]`` where each clause must contain exactly three *different* positive
integers.

The reduction is classic:

* For each vertex ``v`` we create three Boolean variables
  ``X_{v,0}, X_{v,1}, X_{v,2}`` representing that the vertex receives colour
  0, 1 or 2 respectively.  The clause ``(X_{v,0}, X_{v,1}, X_{v,2})`` forces
  exactly one of them to be true – this is precisely a 1‑in‑3 clause.

* For each edge ``(u, v)`` and each colour ``c`` we must forbid the assignment
  that both endpoints receive the same colour.  The clause ``(X_{u,c},
  X_{v,c}, Y_{(u,v),c})`` with a fresh auxiliary variable ``Y`` achieves
  this: the clause is satisfied iff exactly one of the three literals is true.
  Consequently the case where both ``X`` variables are true is impossible,
  while the case where both are false is allowed (by setting ``Y`` to true).
  The auxiliary variable appears in only this clause, so its value is forced
  locally and does not interfere with other constraints.

The construction runs in polynomial time: we introduce ``3n`` variables for the
vertices and ``3|E|`` auxiliary variables, and we create ``n`` clauses for the
vertex colour constraints plus ``3|E|`` clauses for the edge constraints.

The function ``reduce`` implements this transformation and returns an instance
compatible with the ``OneInThreeSat`` definition.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑coloring instance to a 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).  Vertices are numbered ``0 .. n-1``.

    Returns
    -------
    dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` suitable for
        the ``OneInThreeSat`` problem.
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Mapping for vertex‑colour variables: id = v*3 + colour + 1 (1‑based).
    def var_id(v: int, colour: int) -> int:
        return v * 3 + colour + 1

    clauses: List[List[int]] = []

    # Vertex colour constraints: exactly one colour per vertex.
    for v in range(n):
        clauses.append([var_id(v, 0), var_id(v, 1), var_id(v, 2)])

    # Auxiliary variables start after the vertex variables.
    next_var = n * 3 + 1

    # Edge constraints: for each edge and each colour, forbid both endpoints
    # from sharing that colour.
    for u, v in edges:
        for colour in range(3):
            aux = next_var
            next_var += 1
            clauses.append([var_id(u, colour), var_id(v, colour), aux])

    num_vars = next_var - 1  # because next_var points to the first unused id

    return {"num_vars": num_vars, "clauses": clauses}

