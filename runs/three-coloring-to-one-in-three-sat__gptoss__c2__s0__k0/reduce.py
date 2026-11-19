"""Reduction from 3-Coloring to Positive 1-in-3 SAT.

The source problem (ThreeColoring) is defined in ``problems.py`` with the
following instance format::

    {"n": n, "edges": [[u, v], ...]}

The target problem (OneInThreeSat) expects instances of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

All variables are positive integers starting at 1 and each clause must
contain three *different* variables.  A clause is satisfied iff **exactly**
one of its three variables is assigned ``True``.

The classic polynomial‑time reduction works as follows.

* For every vertex ``v`` we introduce three Boolean variables
  ``v_R``, ``v_G`` and ``v_B`` representing the colour assigned to ``v``.
  The clause ``[v_R, v_G, v_B]`` forces exactly one of them to be true –
  i.e. the vertex receives exactly one colour.

* For every edge ``(u, v)`` we must ensure that ``u`` and ``v`` receive
  different colours.  For each colour ``c`` we add a fresh auxiliary
  variable ``a_{uvc}`` and the clause ``[u_c, v_c, a_{uvc}]``.  If both
  ``u_c`` and ``v_c`` were true, the clause would contain at least two true
  literals, which is forbidden.  If both were false, the clause would need
  ``a_{uvc}`` to be true, but the three auxiliary variables for the edge are
  linked by an additional clause ``[a_{uvR}, a_{uvG}, a_{uvB}]`` that forces
  **exactly one** of them to be true.  Consequently, for each edge exactly
  one colour pair ``(u_c, v_c)`` may have a true literal, meaning the two
  endpoints cannot share the same colour.

The construction uses ``3 * n`` vertex‑colour variables and ``3 * |E|``
auxiliary variables, all of which are positive integers.  The reduction
clearly runs in polynomial time.

The ``reduce`` function below implements this transformation.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to a OneInThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).  Vertices are numbered ``0..n-1``.

    Returns
    -------
    dict
        A One‑in‑3‑SAT instance ``{"num_vars": m, "clauses": [...]}`` such
        that the SAT instance is satisfiable iff the original graph is
        3‑colourable.
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Variable indexing:
    #   For vertex i (0‑based) and colour c in {0,1,2} we assign
    #   var_id = 1 + i*3 + c   (R=0, G=1, B=2)
    #   This yields variables 1 .. 3*n.
    def vertex_var(i: int, colour: int) -> int:
        return 1 + i * 3 + colour

    clauses: List[List[int]] = []

    # 1. Exactly‑one‑colour per vertex.
    for i in range(n):
        clauses.append([
            vertex_var(i, 0),  # Red
            vertex_var(i, 1),  # Green
            vertex_var(i, 2),  # Blue
        ])

    # 2. Edge constraints.
    #    We allocate auxiliary variables sequentially after the vertex vars.
    next_var = 3 * n + 1
    for (u, v) in edges:
        # For each colour create an auxiliary variable.
        aux_vars = [next_var, next_var + 1, next_var + 2]
        next_var += 3
        # Clauses linking the two endpoints with the auxiliary variable.
        for colour in range(3):
            clauses.append([
                vertex_var(u, colour),
                vertex_var(v, colour),
                aux_vars[colour],
            ])
        # Clause that forces exactly one of the three auxiliaries to be true.
        clauses.append(aux_vars)

    num_vars = next_var - 1  # highest variable id used

    return {"num_vars": num_vars, "clauses": clauses}

