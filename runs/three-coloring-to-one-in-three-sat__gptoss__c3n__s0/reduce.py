"""Reduction from 3-Coloring to Monotone 1-in-3 SAT.

The source problem is defined in :class:`problems.ThreeColoring` and the
target problem in :class:`problems.OneInThreeSat`.  Both classes only provide
validation helpers – they do **not** contain solvers.  The reduction must be
polynomial time and preserve the answer (yes‑instances map to yes‑instances and
vice‑versa).

Standard reduction (see e.g. Garey & Johnson, *Computers and Intractability*)
works as follows.

* For each vertex ``v`` we create three Boolean variables
  ``v_R, v_G, v_B`` representing the colour chosen for ``v``.  The clause
  ``(v_R, v_G, v_B)`` forces exactly one of them to be true – this is a
  *one‑in‑three* clause because the problem only allows positive literals.

* For each edge ``(u, v)`` and for each colour ``c`` we introduce a fresh
  auxiliary variable ``e_{uv,c}``.  The clause ``(u_c, v_c, e_{uv,c})``
  guarantees that ``u`` and ``v`` cannot both take colour ``c``: if they did,
  the clause would contain two true literals, violating the one‑in‑three
  requirement.  When the colours differ the clause can be satisfied by setting
  the auxiliary variable appropriately, and each auxiliary variable appears in
  exactly one clause, so there is no conflict between clauses.

The constructed formula uses ``3 * n`` vertex variables and ``3 * |E|``
auxiliary variables, i.e. a linear number of variables and clauses.

The ``reduce`` function validates the input, builds the clause list according
to the scheme above and returns a dictionary compatible with the target
problem's instance format.
"""

from __future__ import annotations

from typing import List, Dict

from problems import ThreeColoring, OneInThreeSat

def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a monotone 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph as described in
        ``ThreeColoring`` – keys ``"n"`` and ``"edges"``.

    Returns
    -------
    dict
        An instance of ``OneInThreeSat`` – keys ``"num_vars"`` and
        ``"clauses"``.  The returned instance is guaranteed to be valid
        according to ``OneInThreeSat.validate``.
    """

    # Validate the source instance first – this will raise InvalidInstance if
    # the format is wrong.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    clauses: List[List[int]] = []

    # Mapping: vertex v, colour c (0,1,2) -> variable id (1‑based).
    # Variable ids start at 1.
    def var_vertex(v: int, c: int) -> int:
        return v * 3 + c + 1

    # 1. Vertex colour selection clauses – exactly one colour per vertex.
    for v in range(n):
        clauses.append([var_vertex(v, 0), var_vertex(v, 1), var_vertex(v, 2)])

    # 2. Edge inequality clauses.
    # Keep a counter for auxiliary variables after the vertex variables.
    next_aux = 3 * n + 1
    for u, v in edges:
        for c in range(3):
            aux = next_aux
            next_aux += 1
            clauses.append([var_vertex(u, c), var_vertex(v, c), aux])

    num_vars = next_aux - 1

    # Build the target instance.
    target_instance = {"num_vars": num_vars, "clauses": clauses}
    # Validate the constructed instance before returning.
    OneInThreeSat.validate(target_instance)
    return target_instance

