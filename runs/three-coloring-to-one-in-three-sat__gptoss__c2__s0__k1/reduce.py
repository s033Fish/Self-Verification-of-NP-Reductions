"""Reduction from 3‑Coloring to 1‑in‑3‑SAT.

The source problem (ThreeColoring) expects an instance of the form::

    {"n": number_of_vertices, "edges": [[u, v], ...]}

The target problem (OneInThreeSat) expects an instance of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

All variables are positive integers starting at ``1`` and each clause must
contain **exactly three distinct** variables.  A clause is satisfied when
**exactly one** of its three variables is assigned ``True``.

The reduction is classic and runs in polynomial time:

* For each vertex ``v`` we introduce three Boolean variables
  ``v_R, v_G, v_B`` representing the colour of ``v``.  The clause
  ``[v_R, v_G, v_B]`` forces exactly one of them to be true – i.e. each
  vertex receives exactly one colour.

* For each edge ``(u, v)`` and each colour ``c`` we must forbid the
  situation where both endpoints receive the same colour.  To express the
  constraint ``¬(u_c ∧ v_c)`` using only positive literals we add a fresh
  auxiliary variable ``z`` and the clause ``[u_c, v_c, z]``.  The 1‑in‑3
  semantics then guarantees that ``u_c`` and ``v_c`` cannot both be true
  (otherwise the clause would have at least two true literals).  The
  auxiliary variable simply takes the ``True`` value when both colour
  variables are ``False``.

The construction yields a formula that is satisfiable **iff** the original
graph is 3‑colourable.

The implementation below follows exactly this description.  It does not
invoke any solver and runs in time linear in the size of the input graph.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a OneInThreeSat instance.

    Parameters
    ----------
    instance:
        ``{"n": int, "edges": List[List[int]]}`` – the graph to be coloured.

    Returns
    -------
    Dict[str, Any]
        ``{"num_vars": int, "clauses": List[List[int]]}`` – the constructed
        1‑in‑3‑SAT formula.
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Helper to obtain the variable id for vertex v and colour c (0,1,2).
    def var_id(v: int, colour: int) -> int:
        # Variables are numbered starting at 1.
        return v * 3 + colour + 1

    clauses: List[List[int]] = []

    # 1. Exactly‑one‑colour clause for each vertex.
    for v in range(n):
        clauses.append([var_id(v, 0), var_id(v, 1), var_id(v, 2)])

    # 2. Edge constraints using auxiliary variables.
    next_aux: int = n * 3 + 1  # first auxiliary variable id
    for u, v in edges:
        # The problem statement guarantees u != v and edges are undirected.
        for colour in range(3):
            aux = next_aux
            next_aux += 1
            clauses.append([var_id(u, colour), var_id(v, colour), aux])

    num_vars = next_aux - 1  # last used variable id

    return {"num_vars": num_vars, "clauses": clauses}

