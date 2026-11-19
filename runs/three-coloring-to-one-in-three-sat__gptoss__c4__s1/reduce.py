"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem is :class:`ThreeColoring` (graph 3‑colorability).
The target problem is :class:`OneInThreeSat` (positive 1‑in‑3‑SAT).

For each vertex ``v`` we introduce three Boolean variables ``v_R``,
``v_G`` and ``v_B`` representing the colour of the vertex.  A clause
``[v_R, v_G, v_B]`` forces exactly one of these variables to be true –
exactly one colour per vertex.

For each edge ``(u, v)`` and each colour ``c`` we must forbid the case
that both endpoints receive the same colour.  The clause ``[u_c, v_c, y]``
with a fresh auxiliary variable ``y`` enforces that at most one of the
two colour variables can be true (if both are false the auxiliary must
be true, which is harmless).  No additional constraints are needed for
the auxiliary variables.

The reduction runs in polynomial time and produces a formula that is
yes‑exactly when the original graph is 3‑colourable.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(instance: dict) -> dict:
    """Reduce a 3‑Coloring instance to a 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and
        ``"edges"`` (list of ``[u, v]`` pairs).  The instance is assumed
        to be validated by :class:`ThreeColoring.validate`.

    Returns
    -------
    dict
        A 1‑in‑3‑SAT instance with keys ``"num_vars"`` and ``"clauses"``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Mapping from (vertex, colour) to variable number.  Colours are 0,1,2.
    var_map: Dict[Tuple[int, int], int] = {}
    next_var = 1
    for v in range(n):
        for c in range(3):
            var_map[(v, c)] = next_var
            next_var += 1

    clauses: List[List[int]] = []

    # Vertex colour selection: exactly one colour per vertex.
    for v in range(n):
        clause = [var_map[(v, 0)], var_map[(v, 1)], var_map[(v, 2)]]
        clauses.append(clause)

    # Edge constraints: for each edge and each colour, add a clause with a fresh aux variable.
    for u, v in edges:
        for c in range(3):
            aux = next_var
            next_var += 1
            clause = [var_map[(u, c)], var_map[(v, c)], aux]
            clauses.append(clause)

    return {"num_vars": next_var - 1, "clauses": clauses}

