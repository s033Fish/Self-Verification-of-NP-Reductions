"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem is :class:`ThreeColoring` (undirected graph with vertices
0..n-1).  The target problem is :class:`OneInThreeSat` (positive literals only,
each clause must have exactly one true literal).

For each vertex we create three Boolean variables indicating the colour of the
vertex.  A clause ``[v_R, v_G, v_B]`` forces exactly one of the three colours
to be chosen – this is precisely the "exactly‑one" requirement of a proper
colouring.

For an edge ``(u, v)`` we must forbid the two endpoints from sharing the same
colour.  The following gadget, taken from standard reductions, achieves this
using only 1‑in‑3 clauses:

* For each colour ``c`` (0,1,2) introduce an auxiliary variable ``t_{e,c}``.
* Add the clause ``[u_c, v_c, t_{e,c}]``.  If both ``u_c`` and ``v_c`` are true
  the clause would have two true literals, which is impossible, so the same
  colour on an edge is ruled out.
* Finally add the clause ``[t_{e,0}, t_{e,1}, t_{e,2}]``.  When the endpoints
  have different colours, exactly one of the three ``t`` variables must be
  true, satisfying the clause.  When the colours are equal the instance is
  already unsatisfiable because of the first three clauses.

The construction uses ``3*n + 3*|E|`` variables and ``n + 4*|E|`` clauses, all
polynomial in the size of the input graph.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, OneInThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` describing the input
        graph.  The instance is assumed to be valid according to
        :class:`ThreeColoring.validate`.

    Returns
    -------
    dict
        An instance of :class:`OneInThreeSat` – a dict with keys ``"num_vars"``
        and ``"clauses"``.  The returned instance is guaranteed to be valid
        (passes ``OneInThreeSat.validate``) and satisfies the correctness
        condition: the original graph is 3‑colorable iff the produced formula
        has a 1‑in‑3 satisfying assignment.
    """

    # Validate the source instance – will raise if malformed.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Variable numbering:
    #   For each vertex v (0‑based) we allocate three variables:
    #       v_R = 3*v + 1, v_G = 3*v + 2, v_B = 3*v + 3
    #   For each edge e we allocate three auxiliary variables after the vertex
    #   variables.
    num_vertex_vars = 3 * n
    num_edge_vars = 3 * len(edges)
    num_vars = num_vertex_vars + num_edge_vars

    clauses: List[List[int]] = []

    # 1. Exactly‑one colour per vertex.
    for v in range(n):
        base = 3 * v
        clauses.append([base + 1, base + 2, base + 3])

    # 2. Edge gadgets.
    for e_idx, (u, v) in enumerate(edges):
        # Base index for the three auxiliary variables of this edge.
        t_base = num_vertex_vars + 3 * e_idx  # 0‑based
        # For each colour c = 0,1,2 create clause [u_c, v_c, t_{e,c}]
        for c in range(3):
            u_var = 3 * u + c + 1
            v_var = 3 * v + c + 1
            t_var = t_base + c + 1
            clauses.append([u_var, v_var, t_var])
        # Clause that forces exactly one of the three t‑variables to be true.
        clauses.append([t_base + 1, t_base + 2, t_base + 3])

    # Build the target instance.
    target_instance = {"num_vars": num_vars, "clauses": clauses}

    # Validate the constructed instance.
    OneInThreeSat.validate(target_instance)
    return target_instance

