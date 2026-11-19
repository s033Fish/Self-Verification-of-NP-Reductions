"""Reduction from 3-Coloring to SAT.

The reduction follows the classic polynomial‑time construction:

* For each vertex ``v`` we introduce three Boolean variables
  ``X_{v,1}``, ``X_{v,2}``, ``X_{v,3}`` meaning *v* receives colour 1,2,3.
* Every vertex must receive **at least one** colour – a clause with the three
  positive literals.
* Every vertex must receive **at most one** colour – for each unordered pair
  of colours we add a clause forbidding both to be true simultaneously.
* Adjacent vertices must not share a colour – for each edge ``(u, v)`` and each
  colour ``c`` we add a clause forbidding ``X_{u,c}`` and ``X_{v,c}`` to be
  true together.

The resulting CNF formula is satisfiable iff the original graph is
3‑colorable.  The construction uses exactly ``3 * n`` variables where ``n`` is the
number of vertices.

The module provides a single function ``reduce`` that takes a 3‑Coloring
instance (as defined in ``problems.py``) and returns a SAT instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, Sat


def _var_index(vertex: int, colour: int) -> int:
    """Return the SAT variable number for ``vertex`` coloured ``colour``.

    Variables are numbered from 1 upwards.  For vertex ``v`` (0‑based) and colour
    ``c`` in ``{1, 2, 3}`` we use the encoding ``3 * v + c``.
    """
    return 3 * vertex + colour


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to an equivalent SAT instance.

    The function validates the input using ``ThreeColoring.validate`` and then
    builds the CNF according to the construction described in the module
    docstring.
    """
    # Validate the source instance.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of SAT variables: three per vertex.
    m = 3 * n
    clauses: List[List[int]] = []

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([_var_index(v, 1), _var_index(v, 2), _var_index(v, 3)])

    # 2. Each vertex gets at most one colour (pairwise exclusion).
    for v in range(n):
        # pairs (1,2), (1,3), (2,3)
        clauses.append([-_var_index(v, 1), -_var_index(v, 2)])
        clauses.append([-_var_index(v, 1), -_var_index(v, 3)])
        clauses.append([-_var_index(v, 2), -_var_index(v, 3)])

    # 3. Adjacent vertices cannot share the same colour.
    for u, v in edges:
        for colour in (1, 2, 3):
            clauses.append([-_var_index(u, colour), -_var_index(v, colour)])

    sat_instance: Dict = {"num_vars": m, "clauses": clauses}
    # Validate the produced SAT instance (helps catch programming errors).
    Sat.validate(sat_instance)
    return sat_instance

