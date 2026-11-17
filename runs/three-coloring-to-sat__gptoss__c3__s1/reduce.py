"""Reduction from 3-Coloring to SAT.

The source problem is :class:`ThreeColoring` (graph 3‑colorability) and the
target problem is :class:`Sat` (CNF satisfiability).  The reduction follows the
standard textbook construction:

* For each vertex ``v`` and each colour ``c`` in {0,1,2} we introduce a Boolean
  variable ``x_{v,c}`` meaning *vertex ``v`` receives colour ``c``*.
* Every vertex must receive **at least one** colour – a clause containing the
  three variables for that vertex.
* A vertex cannot receive **two** colours simultaneously – for each unordered
  pair of colours we add a clause ``(¬x_{v,c} ∨ ¬x_{v,d})``.
* Adjacent vertices cannot share a colour – for each edge ``(u,v)`` and each
  colour ``c`` we add a clause ``(¬x_{u,c} ∨ ¬x_{v,c})``.

The variable numbering mirrors the internal helper used by the exact solver in
``problems.py`` (``var(v,c) = 3*v + c + 1``) but any bijection would be fine.

The reduction runs in polynomial time (``O(n + m)`` where ``n`` is the number of
vertices and ``m`` the number of edges) and respects all edge‑cases described in
the problem statements.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse their validation helpers.
from problems import ThreeColoring, Sat


def _var(v: int, c: int) -> int:
    """Return the SAT variable number for vertex ``v`` and colour ``c``.

    Colours are 0,1,2.  The formula used in ``problems.py`` defines the same
    mapping, which keeps the reduction easy to reason about and ensures the
    variable range is exactly ``3 * n``.
    """

    return 3 * v + c + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a graph as described in the docstring of
        :class:`ThreeColoring` – it must contain the keys ``"n"`` and
        ``"edges"``.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [...]}`` that is
        satisfiable iff the input graph is 3‑colorable.
    """

    # Validate the source instance – this raises ``InvalidInstance`` if the
    # format is wrong, matching the contract of a reduction.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of SAT variables: three per vertex.
    num_vars = 3 * n
    clauses: List[List[int]] = []

    # 1. Every vertex gets at least one colour.
    for v in range(n):
        clauses.append([_var(v, 0), _var(v, 1), _var(v, 2)])
        # 2. No vertex gets two colours simultaneously.
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-_var(v, c1), -_var(v, c2)])

    # 3. Adjacent vertices cannot share a colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-_var(u, c), -_var(v, c)])

    result = {"num_vars": num_vars, "clauses": clauses}
    # Validate the produced SAT instance (helps catch bugs).
    Sat.validate(result)
    return result

