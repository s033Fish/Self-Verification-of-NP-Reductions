"""Reduction from 3-Coloring to SAT.

The reduction is the classic polynomial-time transformation:

* For each vertex *v* we introduce three Boolean variables
  ``v_0, v_1, v_2`` indicating whether the vertex receives colour 0, 1 or 2.
* Every vertex must receive **at least one** colour – a clause with the three
  positive literals.
* Every vertex must receive **at most one** colour – for each pair of colours a
  clause with the two negated literals.
* Adjacent vertices must not share the same colour – for each edge ``(u, v)``
  and each colour ``c`` a clause ``(¬u_c ∨ ¬v_c)``.

The resulting CNF formula is satisfiable iff the original graph is
3‑colourable.

The module provides a single public function ``reduce(instance)`` that takes a
valid ``ThreeColoring`` instance (as defined in ``problems.py``) and returns a
valid ``Sat`` instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeColoring, Sat


def _var_index(vertex: int, colour: int) -> int:
    """Return the SAT variable number for ``vertex`` with ``colour``.

    Variables are numbered from 1 upwards as required by the SAT definition.
    ``colour`` is expected to be 0, 1 or 2.
    """
    # Each vertex gets three consecutive variables.
    return vertex * 3 + colour + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a 3‑Coloring instance into an equivalent SAT instance.

    The function assumes ``instance`` is a valid ``ThreeColoring`` description –
    callers (including the provided tests) will invoke ``ThreeColoring.validate``
    beforehand if they wish to guarantee correctness.
    """
    # Validate the source instance using the provided helper.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Total number of SAT variables is three per vertex.
    num_vars = n * 3
    clauses: List[List[int]] = []

    # 1. Each vertex receives at least one colour.
    for v in range(n):
        clause = [_var_index(v, c) for c in range(3)]
        clauses.append(clause)

        # 2. Each vertex receives at most one colour – pairwise mutual exclusion.
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-_var_index(v, c1), -_var_index(v, c2)])

    # 3. Adjacent vertices must not share the same colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-_var_index(u, c), -_var_index(v, c)])

    # Build the SAT instance dictionary.
    sat_instance: Dict[str, Any] = {"num_vars": num_vars, "clauses": clauses}
    # Validate the target instance for safety.
    Sat.validate(sat_instance)  # type: ignore[attr-defined]
    return sat_instance

