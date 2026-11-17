"""Reduction from 3-Coloring to SAT.

The source problem is :class:`ThreeColoring` (graph 3‑colorability) and the
target problem is :class:`Sat` (CNF satisfiability).  The reduction follows the
standard textbook construction:

* For each vertex ``i`` we introduce three Boolean variables ``x_{i,0}``,
  ``x_{i,1}``, ``x_{i,2}`` representing the three possible colours.
* Exactly one of the three variables must be true – encoded by one *at‑least*
  clause and three *at‑most* clauses.
* For every edge ``(u, v)`` we forbid the two endpoints from sharing the same
  colour, i.e. for each colour ``c`` we add the clause ``(~x_{u,c} ∨ ~x_{v,c})``.

The produced CNF uses variables numbered from ``1`` upwards in the order
``3*i + c + 1`` where ``i`` is the vertex index and ``c`` the colour index.
The function validates the input instance using :class:`ThreeColoring.validate`
and returns a dictionary that conforms to the format expected by
``Sat.validate``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, Sat


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph with keys ``"n"`` and ``"edges"`` as
        described in the docstring of :class:`ThreeColoring`.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [...]}`` that is
        satisfiable iff the input graph is 3‑colorable.
    """
    # Validate the source instance first – this will raise ``InvalidInstance``
    # if the format is wrong.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of boolean variables: three per vertex.
    m = 3 * n
    clauses: List[List[int]] = []

    # Helper to map (vertex, colour) to a SAT variable number (1‑based).
    def var(v: int, colour: int) -> int:
        return 3 * v + colour + 1

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # 2. Each vertex gets at most one colour (pairwise exclusion).
    for v in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-var(v, c1), -var(v, c2)])

    # 3. Adjacent vertices must not share a colour.
    for u, w in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(w, c)])

    # Construct the SAT instance dictionary.
    sat_instance = {"num_vars": m, "clauses": clauses}
    # Validate the produced instance (helps catch bugs).
    Sat.validate(sat_instance)
    return sat_instance

