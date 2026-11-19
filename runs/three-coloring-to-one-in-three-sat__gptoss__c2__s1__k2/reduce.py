"""Reduction from 3-Coloring to Positive 1-in-3 SAT.

The source problem (ThreeColoring) expects an instance of the form

    {"n": n, "edges": [[u, v], ...]}

where vertices are numbered 0..n-1 and each edge is an unordered pair
with u != v.

The target problem (OneInThreeSat) expects an instance of the form

    {"num_vars": m, "clauses": [[a, b, c], ...]}

All variables are positive integers 1..m and each clause contains three
*different* variables.  A clause is satisfied iff **exactly one** of its
variables is assigned True.

The classic polynomial‑time reduction works as follows.

* For every vertex v we introduce three Boolean variables
  ``v_R, v_G, v_B`` representing the choice of colour Red, Green or Blue.
  The clause ``[v_R, v_G, v_B]`` forces exactly one of them to be true –
  i.e. each vertex receives exactly one colour.

* For every edge (u, v) we must forbid the two endpoints from sharing the
  same colour.  For each colour c ∈ {R, G, B} we introduce an auxiliary
  variable ``a_{uv,c}``.  The clause ``[u_c, v_c, a_{uv,c}]`` enforces that
  at most one of ``u_c`` and ``v_c`` can be true (if both were true the
  clause would have at least two true literals, violating the 1‑in‑3
  condition).  When neither endpoint uses colour c, the auxiliary must be
  true to satisfy the clause.

* Finally we add the clause ``[a_{uv,R}, a_{uv,G}, a_{uv,B}]``.  Because
  each vertex already selects exactly one colour, the three auxiliary
  variables cannot all be false; exactly one of them will be true – the
  colour that is *unused* by both vertices.  This clause therefore forces
  the three edge‑clauses to be consistent and guarantees that the two
  vertices indeed choose different colours.

The construction uses 3 n vertex variables and 3 |E| auxiliary variables,
so the total number of variables is ``m = 3*n + 3*len(edges)``.  The
number of clauses is ``n`` (vertex colour clauses) plus ``4*len(edges)``
edge‑clauses.

The reduction runs in time linear in the size of the input graph, which
is polynomial.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a OneInThreeSat instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": List[List[int]]}``

    Returns
    -------
    dict
        ``{"num_vars": int, "clauses": List[List[int]]}``
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Variable numbering:
    #   For vertex v (0‑based) we assign three variables:
    #       v_R = 3*v + 1
    #       v_G = 3*v + 2
    #       v_B = 3*v + 3
    #   Auxiliary variables for each edge are numbered after the vertex
    #   variables, in the order they are created.
    clauses: List[List[int]] = []

    # Vertex colour clauses – exactly one colour per vertex.
    for v in range(n):
        vr = 3 * v + 1
        vg = 3 * v + 2
        vb = 3 * v + 3
        clauses.append([vr, vg, vb])

    # Keep track of the next available variable index for auxiliaries.
    next_aux = 3 * n + 1  # first auxiliary variable id

    for (u, v) in edges:
        # Vertex colour variable ids.
        u_r, u_g, u_b = 3 * u + 1, 3 * u + 2, 3 * u + 3
        v_r, v_g, v_b = 3 * v + 1, 3 * v + 2, 3 * v + 3

        # Create three auxiliary variables for this edge.
        a_r = next_aux
        a_g = next_aux + 1
        a_b = next_aux + 2
        next_aux += 3

        # Edge colour‑inequality clauses.
        clauses.append([u_r, v_r, a_r])
        clauses.append([u_g, v_g, a_g])
        clauses.append([u_b, v_b, a_b])
        # Exactly one of the auxiliaries must be true.
        clauses.append([a_r, a_g, a_b])

    num_vars = next_aux - 1  # because next_aux points to the next free id

    return {"num_vars": num_vars, "clauses": clauses}

