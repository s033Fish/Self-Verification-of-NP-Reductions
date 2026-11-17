"""Reduction from 3-Coloring to 1-in-3-SAT.

The reduction follows the classic construction used to prove that
1-in-3-SAT is NP‑complete.  For each vertex ``v`` we introduce three
boolean variables ``v_R, v_G, v_B`` indicating whether ``v`` receives the
corresponding colour.  For each vertex we add a clause that forces exactly
one of those three variables to be true – this is precisely a 1‑in‑3 clause.

For each edge ``(u, v)`` we introduce three fresh auxiliary variables
``e_R, e_G, e_B``.  The clause ``[e_R, e_G, e_B]`` forces exactly one of
them to be true.  Finally, for every colour ``c`` we add the clause
``[u_c, v_c, e_c]``.  If both endpoints tried to take the same colour, the
corresponding clause would contain at least two true literals, which is
forbidden.  Conversely, if the endpoints have different colours the
construction can be satisfied by setting the auxiliary variable of the
remaining colour to true.

The function ``reduce`` receives a 3‑Coloring instance (a dict with keys
``"n"`` and ``"edges"``) and returns a 1‑in‑3‑SAT instance in the format
required by :class:`OneInThreeSat` – a dict with ``"num_vars"`` and
``"clauses"``.

The reduction runs in polynomial time: the number of variables and
clauses is linear in ``n`` and the number of edges.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# The problem classes are defined in ``problems.py``.  Importing only the
# validation helpers ensures that the instance we produce conforms to the
# expected format.
from problems import OneInThreeSat, ThreeColoring


def reduce(instance: Dict) -> Dict:
    """Reduce a ``ThreeColoring`` instance to a ``OneInThreeSat`` instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).  The instance is assumed to be valid –
        ``ThreeColoring.validate`` can be called to raise an exception for
        malformed input.

    Returns
    -------
    dict
        A ``OneInThreeSat`` instance (``{"num_vars": m, "clauses": [...]}``).
    """

    # Validate the source instance – this will raise ``InvalidInstance`` if
    # the input does not respect the specification.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Mapping from (vertex, colour) to variable id.  Colours are indexed 0,1,2.
    # Variable ids start at 1.
    var_id = 1
    vertex_colour_var: Dict[Tuple[int, int], int] = {}
    for v in range(n):
        for colour in range(3):
            vertex_colour_var[(v, colour)] = var_id
            var_id += 1

    # Mapping for auxiliary edge variables (edge index, colour) -> var id.
    edge_colour_var: Dict[Tuple[int, int], int] = {}
    for e_idx, _ in enumerate(edges):
        for colour in range(3):
            edge_colour_var[(e_idx, colour)] = var_id
            var_id += 1

    num_vars = var_id - 1
    clauses: List[List[int]] = []

    # Vertex colour uniqueness: exactly one colour per vertex.
    for v in range(n):
        clause = [vertex_colour_var[(v, c)] for c in range(3)]
        clauses.append(clause)

    # Edge constraints.
    for e_idx, (u, v) in enumerate(edges):
        # Exactly one auxiliary variable for the edge.
        aux_clause = [edge_colour_var[(e_idx, c)] for c in range(3)]
        clauses.append(aux_clause)
        # For each colour, the clause (u_c, v_c, e_c).
        for colour in range(3):
            clause = [
                vertex_colour_var[(u, colour)],
                vertex_colour_var[(v, colour)],
                edge_colour_var[(e_idx, colour)],
            ]
            clauses.append(clause)

    # Validate the constructed target instance.
    target_instance = {"num_vars": num_vars, "clauses": clauses}
    OneInThreeSat.validate(target_instance)
    return target_instance

