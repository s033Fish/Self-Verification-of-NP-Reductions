"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem is ``ThreeColoring`` defined in ``problems.py``.  An
instance is a dictionary ``{"n": n, "edges": [[u, v], ...]}`` where the
vertices are numbered ``0..n-1``.

The target problem is ``OneInThreeSat`` – a positive 1‑in‑3 SAT formula.
An instance is a dictionary ``{"num_vars": m, "clauses": [[a, b, c], ...]}``
where each clause contains three *different* positive integers.

The reduction is classic:

* For each vertex ``v`` we create three Boolean variables
  ``v_R, v_G, v_B`` (encoded as a single integer each).  The clause
  ``[v_R, v_G, v_B]`` forces exactly one of them to be true – i.e. each
  vertex receives exactly one colour.

* For each edge ``(u, v)`` we introduce three fresh auxiliary variables
  ``s_{e,0}, s_{e,1}, s_{e,2}`` (one per colour).  For colour ``c`` we add
  the clause ``[u_c, v_c, s_{e,c}]``.  If both endpoints used the same
  colour, the clause would have two true literals – impossible for a
  1‑in‑3 clause.  Hence the endpoints cannot share a colour.

  The auxiliary variables are tied together by the clause
  ``[s_{e,0}, s_{e,1}, s_{e,2}]`` which forces exactly one of them to be
  true.  This guarantees that for each edge exactly one colour is *absent*
  from both endpoints, i.e. the two endpoints use two distinct colours.

The construction uses ``3*n + 3*|E|`` variables and a linear number of
clauses, therefore it runs in polynomial time.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeColoring, OneInThreeSat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeColoring`` format.

    Returns
    -------
    dict
        An instance of ``OneInThreeSat`` that is satisfiable iff the input
        graph is 3‑colorable.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of variables: three per vertex plus three per edge.
    m = 3 * n + 3 * len(edges)
    clauses: List[List[int]] = []

    # Helper to compute variable id for a vertex colour.
    def var_vertex(v: int, colour: int) -> int:
        # colour in {0,1,2}
        return v * 3 + colour + 1  # 1‑based indexing for SAT variables

    # Helper for auxiliary variables of an edge.
    def var_aux(edge_index: int, colour: int) -> int:
        # edge_index enumerates edges in the order given.
        base = 3 * n + edge_index * 3
        return base + colour + 1

    # 1. Exactly‑one‑colour clause for each vertex.
    for v in range(n):
        clause = [var_vertex(v, 0), var_vertex(v, 1), var_vertex(v, 2)]
        clauses.append(clause)

    # 2. Edge constraints.
    for ei, (u, v) in enumerate(edges):
        # For each colour add the clause [u_c, v_c, s_{e,c}]
        for colour in range(3):
            clause = [var_vertex(u, colour), var_vertex(v, colour), var_aux(ei, colour)]
            clauses.append(clause)
        # Finally the clause linking the three auxiliary variables.
        aux_clause = [var_aux(ei, 0), var_aux(ei, 1), var_aux(ei, 2)]
        clauses.append(aux_clause)

    # Build the target instance.
    result: Dict[str, Any] = {"num_vars": m, "clauses": clauses}
    # Validate the produced instance to catch programming errors.
    OneInThreeSat.validate(result)
    return result

