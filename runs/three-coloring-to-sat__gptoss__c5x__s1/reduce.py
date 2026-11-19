"""Reduction from 3-Coloring to SAT.

The source problem is :class:`ThreeColoring` defined in ``problems.py``.
The target problem is :class:`Sat` defined in the same file.

For a graph with ``n`` vertices we create three boolean variables for each
vertex – one for each colour.  Variable numbers start at ``1`` (as required
by the SAT format) and are assigned as ``v = i * 3 + c + 1`` where ``i`` is
the vertex index (0‑based) and ``c`` is the colour index (0,1,2).

Constraints encoded as CNF clauses:

* **At least one colour per vertex** – a clause ``(v_i0 ∨ v_i1 ∨ v_i2)``.
* **At most one colour per vertex** – for each pair of colours a clause
  ``(¬v_ic ∨ ¬v_id)``.
* **Adjacent vertices differ in colour** – for each edge ``(u, v)`` and
  each colour ``c`` a clause ``(¬v_uc ∨ ¬v_vc)``.

The resulting formula is satisfiable iff the original graph is 3‑colourable.
The construction is polynomial‑time and works for all edge cases described
in the problem statements.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, Sat


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` representing the
        undirected graph.

    Returns
    -------
    dict
        A SAT instance in the format ``{"num_vars": m, "clauses": [...]}``.
    """
    # Validate the source instance using the provided helper.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of SAT variables: three per vertex.
    m = 3 * n
    clauses: List[List[int]] = []

    # Helper to get the variable number for vertex i and colour c (0‑based).
    def var(i: int, c: int) -> int:
        return i * 3 + c + 1  # SAT variables are 1‑based

    # 1. Each vertex receives at least one colour.
    for i in range(n):
        clauses.append([var(i, 0), var(i, 1), var(i, 2)])

    # 2. Each vertex receives at most one colour (pairwise mutual exclusion).
    for i in range(n):
        # colour pairs (0,1), (0,2), (1,2)
        clauses.append([-var(i, 0), -var(i, 1)])
        clauses.append([-var(i, 0), -var(i, 2)])
        clauses.append([-var(i, 1), -var(i, 2)])

    # 3. Adjacent vertices must not share the same colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    # Validate the produced SAT instance before returning.
    Sat.validate({"num_vars": m, "clauses": clauses})
    return {"num_vars": m, "clauses": clauses}
