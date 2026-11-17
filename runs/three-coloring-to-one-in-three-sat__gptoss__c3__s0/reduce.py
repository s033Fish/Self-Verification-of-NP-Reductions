"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem is ``ThreeColoring`` (graph 3‑colorability) and the
target problem is ``OneInThreeSat`` (positive 1‑in‑3 SAT).  The reduction is
polynomial‑time and follows the classic construction used in many textbooks:

* For each vertex *v* we create three Boolean variables
  ``v_R, v_G, v_B`` meaning that *v* receives the corresponding colour.
  The clause ``[v_R, v_G, v_B]`` forces exactly one of them to be true – this
  is a direct 1‑in‑3 clause.

* For each edge ``(u, v)`` and each colour ``c`` we introduce an auxiliary
  variable ``z_{uv}^c``.  The clause ``[u_c, v_c, z_{uv}^c]`` together with the
  clause ``[z_{uv}^R, z_{uv}^G, z_{uv}^B]`` ensures that the two endpoints do
  not share the same colour.  Intuitively, if both ``u_c`` and ``v_c`` were
  true, the first clause would already have two true literals, which is
  forbidden; the only way to satisfy it is to set ``z_{uv}^c`` to false.  The
  last clause then forces exactly one of the three auxiliary variables to be
  true, guaranteeing that at most one colour is shared on the edge.

The construction uses only positive literals, each clause contains three
distinct variables, and the number of variables and clauses is linear in the
size of the input graph, so the reduction runs in polynomial time.
"""

from __future__ import annotations

from typing import List, Dict

# Import problem definitions for validation (optional) and to expose the
# expected classes to the verifier.
from problems import ThreeColoring, OneInThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a positive 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph as defined by ``ThreeColoring`` –
        ``{"n": n, "edges": [[u, v], ...]}``.

    Returns
    -------
    dict
        An instance of ``OneInThreeSat`` – ``{"num_vars": m, "clauses": [...]}``.
    """
    # Validate the source instance (raises InvalidInstance if malformed).
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Mapping (vertex, colour) -> variable index (1‑based as required by the SAT
    # format). Colours are 0,1,2 representing the three colours.
    var_index: Dict[tuple[int, int], int] = {}
    next_var = 1
    for v in range(n):
        for colour in range(3):
            var_index[(v, colour)] = next_var
            next_var += 1

    # Auxiliary variables for each edge and colour.
    aux: Dict[tuple[int, int, int], int] = {}
    for (u, v) in edges:
        for colour in range(3):
            aux[(u, v, colour)] = next_var
            next_var += 1

    clauses: List[List[int]] = []

    # Vertex colour selection: exactly one colour per vertex.
    for v in range(n):
        clause = [var_index[(v, 0)], var_index[(v, 1)], var_index[(v, 2)]]
        clauses.append(clause)

    # Edge constraints.
    for (u, v) in edges:
        edge_aux_vars = []
        for colour in range(3):
            uv_aux = aux[(u, v, colour)]
            edge_aux_vars.append(uv_aux)
            clause = [
                var_index[(u, colour)],
                var_index[(v, colour)],
                uv_aux,
            ]
            clauses.append(clause)
        # Exactly one of the three auxiliary variables must be true.
        clauses.append(edge_aux_vars)

    num_vars = next_var - 1
    reduced_instance = {"num_vars": num_vars, "clauses": clauses}
    # Optional sanity check – validates the target instance format.
    OneInThreeSat.validate(reduced_instance)
    return reduced_instance

