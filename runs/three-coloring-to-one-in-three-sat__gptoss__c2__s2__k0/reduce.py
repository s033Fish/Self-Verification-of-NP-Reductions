"""Reduction from 3-Coloring to 1-in-3-SAT.

The source problem (ThreeColoring) expects an instance of the form::

    {"n": <number of vertices>, "edges": [[u, v], ...]}

Vertices are numbered 0..n-1 and each edge is an undirected pair.

The target problem (OneInThreeSat) expects an instance of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

Variables are numbered starting at 1 and each clause must contain three
distinct positive integers.  A clause is satisfied iff **exactly one**
of its three variables is assigned ``True``.

The reduction creates three Boolean variables for each vertex – one for
each colour (red, green, blue).  A vertex clause ``[v_R, v_G, v_B]`` forces
exactly one colour to be chosen for that vertex.  For every edge ``(u, v)``
and for each colour we add a clause ``[u_c, v_c, w]`` where ``w`` is a fresh
auxiliary variable.  This clause is satisfied exactly when *at most* one of
``u_c`` and ``v_c`` is true (the auxiliary variable can be set to true when
both are false).  Consequently the clause forbids the two adjacent vertices
from sharing the same colour.

The construction runs in polynomial time: it creates ``3n`` colour
variables, ``n`` vertex clauses and ``3|E|`` edge clauses, introducing one
new auxiliary variable per edge‑colour combination.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a OneInThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        ``[u, v]`` pairs).  The format follows the definition in
        ``problems.py`` for the ``ThreeColoring`` class.

    Returns
    -------
    dict
        A dictionary representing a 1‑in‑3‑SAT formula with keys
        ``"num_vars"`` and ``"clauses"``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Helper to map a vertex and a colour (0,1,2) to a variable index.
    # Variables are 1‑based, so we add 1.
    def var(v: int, colour: int) -> int:
        return v * 3 + colour + 1

    clauses: List[List[int]] = []

    # Vertex colour selection: exactly one of the three colours per vertex.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Edge constraints: adjacent vertices cannot share a colour.
    # For each colour we introduce a fresh auxiliary variable.
    next_aux = 3 * n + 1  # first auxiliary variable index
    for u, v in edges:
        for colour in range(3):
            aux = next_aux
            next_aux += 1
            clauses.append([var(u, colour), var(v, colour), aux])

    num_vars = next_aux - 1  # last used variable index

    return {"num_vars": num_vars, "clauses": clauses}

