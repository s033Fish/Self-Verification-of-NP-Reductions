"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem is :class:`ThreeColoring` defined in ``problems.py``.
The target problem is :class:`OneInThreeSat` defined in the same file.

For a graph G = (V, E) we create Boolean variables ``v_c`` for each
vertex ``v`` and each colour ``c`` in {0, 1, 2}.  The variable is true iff
the vertex receives that colour.  For each vertex we add a clause
``[v_0, v_1, v_2]`` which forces exactly one of the three colour variables
to be true – this is precisely a 1‑in‑3 clause.

For each edge ``(u, v)`` and each colour ``c`` we introduce an auxiliary
variable ``a_{u,v,c}``.  The clause ``[u_c, v_c, a_{u,v,c}]`` enforces that
the two endpoints cannot both be coloured ``c``: if both were true the
clause would have two true literals, which is forbidden.  If exactly one
endpoint has colour ``c`` the auxiliary variable can be false, and if
neither endpoint has colour ``c`` the auxiliary variable can be true.

The construction is polynomial in the size of the input graph and is
correct: a proper 3‑colouring yields a satisfying assignment for the
produced 1‑in‑3‑SAT instance and any satisfying assignment of the 1‑in‑3‑
SAT instance defines a proper 3‑colouring of the original graph.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import ThreeColoring, OneInThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ``ThreeColoring`` format:
        ``{"n": n, "edges": [[u, v], ...]}``.

    Returns
    -------
    dict
        An instance of ``OneInThreeSat``: ``{"num_vars": m, "clauses": [...]}``.
    """
    # Validate the source instance (will raise if malformed).
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Variable indexing: start at 1 as required by the target format.
    # For each vertex v and colour c (0,1,2) we allocate a variable.
    # We'll store them in a dict for easy lookup.
    var_vertex_colour: Dict[Tuple[int, int], int] = {}
    next_var = 1
    for v in range(n):
        for c in range(3):
            var_vertex_colour[(v, c)] = next_var
            next_var += 1

    # Auxiliary variables for each edge and colour.
    var_aux: Dict[Tuple[int, int, int], int] = {}
    for (u, v) in edges:
        for c in range(3):
            var_aux[(u, v, c)] = next_var
            next_var += 1

    clauses: List[List[int]] = []

    # Vertex colour clauses: exactly one colour per vertex.
    for v in range(n):
        clause = [var_vertex_colour[(v, 0)], var_vertex_colour[(v, 1)], var_vertex_colour[(v, 2)]]
        clauses.append(clause)

    # Edge colour inequality clauses.
    for (u, v) in edges:
        for c in range(3):
            clause = [
                var_vertex_colour[(u, c)],
                var_vertex_colour[(v, c)],
                var_aux[(u, v, c)],
            ]
            clauses.append(clause)

    target_instance = {"num_vars": next_var - 1, "clauses": clauses}
    # Validate the constructed target instance.
    OneInThreeSat.validate(target_instance)
    return target_instance

