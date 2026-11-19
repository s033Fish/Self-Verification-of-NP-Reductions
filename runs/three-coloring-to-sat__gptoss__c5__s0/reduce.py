"""Reduction from 3-Coloring to SAT.

The source problem is :class:`ThreeColoring` defined in ``problems.py``.
The target problem is :class:`Sat` defined in the same file.

For each vertex ``i`` (0‑based) we introduce three Boolean variables
``x_{i,0}``, ``x_{i,1}``, ``x_{i,2}`` meaning that vertex ``i`` receives
colour 0, 1 or 2 respectively.  Variables are numbered from 1 as required
by the SAT instance format:

    var_id = i * 3 + colour + 1

The CNF consists of three groups of clauses:

* **At least one colour** per vertex – a single clause with the three
  positive literals.
* **At most one colour** per vertex – for each unordered pair of colours
  we add a clause ``(-x_{i,c} ∨ -x_{i,d})``.
* **Edge constraints** – for every edge ``(u, v)`` and every colour ``c``
  we add a clause ``(-x_{u,c} ∨ -x_{v,c})`` ensuring adjacent vertices do
  not share the same colour.

The construction is polynomial in the size of the graph (O(|V|+|E|)).
If the original graph is 3‑colourable then the SAT formula is satisfiable
and vice‑versa.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, Sat


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph as defined by ``ThreeColoring``.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the source instance using the provided helper.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of SAT variables: three per vertex.
    num_vars = 3 * n
    clauses: List[List[int]] = []

    # Helper to compute variable id for vertex i and colour c (0,1,2).
    def var(i: int, c: int) -> int:
        return i * 3 + c + 1  # SAT variables are 1‑based

    # 1. Each vertex gets at least one colour.
    for i in range(n):
        clauses.append([var(i, 0), var(i, 1), var(i, 2)])

    # 2. Each vertex gets at most one colour (pairwise exclusion).
    for i in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-var(i, c1), -var(i, c2)])

    # 3. Adjacent vertices cannot share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    # Validate the constructed SAT instance.
    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

