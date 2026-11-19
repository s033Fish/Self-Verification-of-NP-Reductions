"""Reduction from 3-Coloring to SAT.

The source problem is :class:`ThreeColoring` defined in ``problems.py``.
The target problem is :class:`Sat`.

For each vertex ``v`` (0‑based) we create three Boolean variables that
represent the statement "vertex ``v`` receives colour ``c``" where
``c`` is 0,1,2 (corresponding to the three colours).  The variable index
in the SAT instance is ``v * 3 + c + 1`` because SAT variables are
1‑based.

Constraints encoded as CNF clauses:

* **Exactly one colour per vertex** – at least one colour:
  ``(v0 ∨ v1 ∨ v2)`` and at most one colour pairwise:
  ``(¬v0 ∨ ¬v1)``, ``(¬v0 ∨ ¬v2)``, ``(¬v1 ∨ ¬v2)``.

* **Adjacent vertices must differ** – for each edge ``(u, v)`` and each
  colour ``c`` we add ``(¬u_c ∨ ¬v_c)``.

The construction runs in time polynomial in the size of the input
graph (``O(n + |E|)`` clauses) and uses ``3n`` variables.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, Sat


def _var_index(vertex: int, colour: int) -> int:
    """Return the SAT variable number for ``vertex`` and ``colour``.

    ``colour`` must be 0, 1 or 2.  SAT variables are 1‑based, so we add 1.
    """
    return vertex * 3 + colour + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an equivalent SAT instance.

    The returned dictionary follows the format required by :class:`Sat`:
    ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
    """
    # Validate the source instance using the provided helper.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of SAT variables: three per vertex.
    num_vars = n * 3
    clauses: List[List[int]] = []

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clause = [_var_index(v, c) for c in range(3)]
        clauses.append(clause)

        # 2. At most one colour: pairwise negative clauses.
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-_var_index(v, c1), -_var_index(v, c2)])

    # 3. Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-_var_index(u, c), -_var_index(v, c)])

    sat_instance = {"num_vars": num_vars, "clauses": clauses}
    # Validate the produced SAT instance.
    Sat.validate(sat_instance)
    return sat_instance

