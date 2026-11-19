"""Reduction from 3-Coloring to Positive 1-in-3 SAT.

The reduction uses a standard gadget construction:

* For each vertex *v* we introduce three Boolean variables ``v_0, v_1, v_2``
  representing the three possible colours. The clause ``[v_0, v_1, v_2]``
  forces exactly one of them to be true (the 1‑in‑3 condition).

* For each edge ``(u, v)`` and each colour ``c`` we introduce a fresh dummy
  variable ``d_{u,v,c}``. The clause ``[u_c, v_c, d_{u,v,c}]`` guarantees that
  ``u_c`` and ``v_c`` cannot both be true – otherwise the clause would have
  at least two true literals, violating the 1‑in‑3 rule.  The dummy variable
  simply takes the value ``True`` when both endpoint colour‑variables are
  false.

All literals are positive, satisfying the target problem's requirement.
The construction is polynomial: it creates ``3·n`` vertex variables and
``3·|E|`` dummy variables, for a total of ``m = 3·n + 3·|E|`` variables, and
``n + 3·|E|`` clauses.

The ``reduce`` function validates the input using ``ThreeColoring.validate``
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
        A dictionary with keys ``"n"`` and ``"edges"`` describing an
        undirected graph as defined by :class:`ThreeColoring`.

    Returns
    -------
    dict
        An instance of :class:`OneInThreeSat` with keys ``"num_vars"`` and
        ``"clauses"``.
    """
    # Validate the source instance – raises InvalidInstance if malformed.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Helper to map a vertex and colour to a SAT variable index (1‑based).
    def vertex_var(v: int, colour: int) -> int:
        # Three variables per vertex, colours 0,1,2.
        return 3 * v + colour + 1

    clauses: List[List[int]] = []

    # 1. For each vertex, enforce exactly one colour via a 1‑in‑3 clause.
    for v in range(n):
        clauses.append([vertex_var(v, 0), vertex_var(v, 1), vertex_var(v, 2)])

    # 2. Edge constraints: for each edge and each colour, add a clause
    #    (u_c, v_c, d) with a fresh dummy variable d.
    dummy_counter = 0
    for u, v in edges:
        for colour in range(3):
            dummy_counter += 1
            dummy_var = 3 * n + dummy_counter  # after vertex variables
            clauses.append([vertex_var(u, colour), vertex_var(v, colour), dummy_var])

    num_vars = 3 * n + dummy_counter
    target_instance = {"num_vars": num_vars, "clauses": clauses}
    # Validate the generated target instance.
    OneInThreeSat.validate(target_instance)
    return target_instance

