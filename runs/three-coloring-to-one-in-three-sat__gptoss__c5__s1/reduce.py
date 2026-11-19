"""Reduction from 3-Coloring to Positive 1-in-3 SAT.

The reduction is polynomial time and follows a standard textbook construction.

For each vertex *v* we create three Boolean variables representing the three
possible colours:

    v_R, v_G, v_B   (indices 3*v+1, 3*v+2, 3*v+3)

The clause ``[v_R, v_G, v_B]`` forces *exactly one* of the three variables to
be true, which encodes that the vertex receives exactly one colour.

For each edge *(u, v)* we introduce three fresh auxiliary variables
``a_uv, b_uv, c_uv``.  The following four clauses are added:

    [u_R, v_R, a_uv]
    [u_G, v_G, b_uv]
    [u_B, v_B, c_uv]
    [a_uv, b_uv, c_uv]

If ``u`` and ``v`` receive the same colour, the first (or second or third)
clause would contain two true literals, which is impossible for a 1‑in‑3
clause.  If the colours differ, exactly one of ``a_uv, b_uv, c_uv`` becomes
true, satisfying the final clause.  Hence the edge constraints are correctly
encoded.

The function ``reduce`` validates the input using ``ThreeColoring.validate``
and returns a dictionary compatible with ``OneInThreeSat``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, OneInThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a Positive 1‑in‑3 SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` as described in the
        ``ThreeColoring`` docstring.

    Returns
    -------
    dict
        An instance of ``OneInThreeSat`` with keys ``"num_vars"`` and
        ``"clauses"``.
    """
    # Validate source instance first – will raise InvalidInstance on error.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    clauses: List[List[int]] = []

    # Helper to map a vertex and colour index to a variable number.
    # Colours are ordered as 0: R, 1: G, 2: B.
    def var(v: int, colour: int) -> int:
        return 3 * v + colour + 1  # +1 because variables start at 1

    # 1. Exactly‑one‑of‑three colour clause for each vertex.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # 2. Edge gadgets.
    # Auxiliary variables start after the vertex variables.
    next_aux = 3 * n + 1
    for (u, v) in edges:
        # allocate three fresh aux variables for this edge
        a = next_aux
        b = next_aux + 1
        c = next_aux + 2
        next_aux += 3

        # colour‑matching clauses
        clauses.append([var(u, 0), var(v, 0), a])  # red
        clauses.append([var(u, 1), var(v, 1), b])  # green
        clauses.append([var(u, 2), var(v, 2), c])  # blue
        # auxiliary clause ensuring exactly one of a,b,c is true
        clauses.append([a, b, c])

    num_vars = next_aux - 1  # the highest variable index used

    # Build the target instance and validate it before returning.
    reduced_instance = {"num_vars": num_vars, "clauses": clauses}
    OneInThreeSat.validate(reduced_instance)
    return reduced_instance

