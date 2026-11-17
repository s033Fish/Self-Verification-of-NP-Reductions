"""Reduction from 3-Coloring to SAT.

The source problem is defined by the ``ThreeColoring`` class in ``problems.py``.
An instance is a dictionary ``{"n": n, "edges": [[u, v], ...]}`` where vertices
are numbered ``0..n-1`` and ``edges`` is a list of undirected simple edges.

The target problem is SAT as defined by the ``Sat`` class.  An instance is a
dictionary ``{"num_vars": m, "clauses": [[literal, ...], ...]}`` where a literal
is a signed integer ``+v`` (variable ``v`` is true) or ``-v`` (false).  Variables
are numbered from ``1`` to ``m``.

The classic polynomial‑time reduction introduces a Boolean variable ``x_{v,c}``
for every vertex ``v`` and colour ``c`` in ``{1,2,3}``.  The variable number is
``v*3 + c`` (1‑based, because SAT variables start at 1).

Constraints encoded as clauses:

* **At least one colour** for each vertex ``v``:
  ``(x_{v,1} ∨ x_{v,2} ∨ x_{v,3})``
* **At most one colour** for each vertex ``v``:
  for each pair of distinct colours ``c1 < c2`` add ``(¬x_{v,c1} ∨ ¬x_{v,c2})``
* **Edge constraint** – adjacent vertices cannot share a colour:
  for each edge ``(u, v)`` and each colour ``c`` add ``(¬x_{u,c} ∨ ¬x_{v,c})``

The resulting SAT instance is satisfiable iff the original graph is
3‑colourable.  The construction works for all edge‑cases described in the
docstring (empty graph, ``n ≤ 3``, etc.).
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse their validation helpers if desired.
from problems import ThreeColoring, Sat


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A valid 3‑Coloring instance (as described in ``ThreeColoring``).

    Returns
    -------
    dict
        A SAT instance suitable for ``Sat.is_yes``.
    """
    # Validate source instance – raises InvalidInstance on malformed input.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of SAT variables = 3 per vertex.  For n = 0 this correctly yields 0.
    num_vars = n * 3
    clauses: List[List[int]] = []

    def var(v: int, colour: int) -> int:
        """Return the SAT variable number for vertex ``v`` and colour ``colour``.

        ``colour`` is in {1,2,3}.  SAT variables are 1‑based, so we compute
        ``v*3 + colour``.
        """
        return v * 3 + colour

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([var(v, 1), var(v, 2), var(v, 3)])

    # 2. Each vertex gets at most one colour (pairwise exclusion).
    for v in range(n):
        clauses.append([-var(v, 1), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 3)])
        clauses.append([-var(v, 2), -var(v, 3)])

    # 3. Adjacent vertices cannot share a colour.
    for u, w in edges:
        for c in (1, 2, 3):
            clauses.append([-var(u, c), -var(w, c)])

    sat_instance = {"num_vars": num_vars, "clauses": clauses}
    # Optional validation of the generated SAT instance.
    Sat.validate(sat_instance)
    return sat_instance

