"""Reduction from 3-Coloring to SAT.

The reduction is the classic polynomial‑time transformation:

* For each vertex *v* we create three Boolean variables
  ``x_{v,0}``, ``x_{v,1}``, ``x_{v,2}`` meaning that *v* receives colour 0,1,2.
* Exactly‑one‑colour constraints are encoded with:
  - a clause ``(x_{v,0} ∨ x_{v,1} ∨ x_{v,2})`` (at least one colour),
  - for each pair of colours a clause ``(¬x_{v,i} ∨ ¬x_{v,j})`` (no two colours).
* For every edge ``(u, v)`` we forbid the two endpoints from sharing a colour:
  for each colour ``c`` we add ``(¬x_{u,c} ∨ ¬x_{v,c})``.

The resulting CNF is satisfiable iff the original graph is 3‑colourable.

The implementation follows the instance format defined in ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs). The instance is validated using
        ``ThreeColoring.validate``.

    Returns
    -------
    dict
        A SAT instance in the format ``{"num_vars": m, "clauses": [...]}``.
    """
    # Validate the source instance – this raises InvalidInstance on malformed input.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Each vertex gets three variables. Variable numbering starts at 1.
    # Variable for vertex v and colour c is 3*v + c + 1 (c in {0,1,2}).
    def var(v: int, c: int) -> int:
        return 3 * v + c + 1

    clauses: List[List[int]] = []

    # 1. Each vertex must have at least one colour.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

        # 2. No vertex may have two colours simultaneously.
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-var(v, c1), -var(v, c2)])

    # 3. Adjacent vertices cannot share the same colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    num_vars = 3 * n
    return {"num_vars": num_vars, "clauses": clauses}

