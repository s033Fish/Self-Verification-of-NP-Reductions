"""Reduction from 3-Coloring to Positive 1-in-3 SAT.

The source problem (ThreeColoring) expects an instance of the form
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1.

The target problem (OneInThreeSat) expects an instance of the form
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where variables are numbered 1..m and each clause contains three
distinct positive integers.  A clause is satisfied iff exactly one of
its three variables is assigned True.

Reduction sketch (standard textbook construction):

* For each vertex *v* we create three Boolean variables representing the
  three possible colours: ``v_R``, ``v_G`` and ``v_B``.  A clause
  ``[v_R, v_G, v_B]`` forces exactly one of them to be true, i.e. the
  vertex receives exactly one colour.

* For each edge *(u, v)* and for each colour *c* ∈ {R,G,B} we create an
  auxiliary variable ``e_{uvc}``.  We add the clause
  ``[u_c, v_c, e_{uvc}]``.  This clause guarantees that the two endpoints
  are not both coloured *c*: if both ``u_c`` and ``v_c`` were true the
  clause would have two true literals, which is forbidden.  If exactly
  one of ``u_c`` or ``v_c`` is true then ``e_{uvc}`` must be false; if
  neither is true then ``e_{uvc}`` must be true.

* Finally we add a clause ``[e_{uvR}, e_{uvG}, e_{uvB}]`` for the same
  edge.  Because each vertex has exactly one colour, exactly one of the
  three colour‑specific edge‑clauses will have both endpoint literals false,
  forcing the corresponding auxiliary variable to be true.  The final
  clause therefore has exactly one true literal and is satisfied.

The construction is polynomial: we introduce 3·n vertex variables and
3·|E| auxiliary variables, yielding at most 4·|E|+n clauses.

The ``reduce`` function implements this transformation.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a OneInThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and
        ``"edges"`` (list of ``[u, v]`` pairs).

    Returns
    -------
    dict
        A OneInThreeSat instance with keys ``"num_vars"`` and
        ``"clauses"``.
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    clauses: List[List[int]] = []

    # Mapping: for vertex i, colour 0->R,1->G,2->B, variable index = 3*i + colour + 1
    def var_vertex(i: int, colour: int) -> int:
        return 3 * i + colour + 1

    # Vertex colour clauses: exactly one of the three colours per vertex
    for i in range(n):
        clauses.append([var_vertex(i, 0), var_vertex(i, 1), var_vertex(i, 2)])

    # Auxiliary variables start after the vertex variables
    next_var = 3 * n + 1

    for (u, v) in edges:
        # Create three auxiliary vars for the three colours
        aux_vars = []
        for colour in range(3):
            aux = next_var
            next_var += 1
            aux_vars.append(aux)
            # Clause linking the two endpoints with the auxiliary variable
            clauses.append([var_vertex(u, colour), var_vertex(v, colour), aux])
        # Clause that forces exactly one of the auxiliaries to be true
        clauses.append(aux_vars)

    num_vars = next_var - 1  # because next_var is one past the last used

    return {"num_vars": num_vars, "clauses": clauses}

