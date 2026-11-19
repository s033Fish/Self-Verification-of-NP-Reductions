"""Reduction from 3-Coloring to SAT.

The source problem is defined by :class:`benchmark.problems.three_coloring.ThreeColoring`
which expects an instance `{"n": n, "edges": [[u, v], ...]}`.  The target
problem is generic CNF SAT, defined by :class:`benchmark.problems.sat.Sat`
with the instance format `{"num_vars": m, "clauses": [[literal, ...], ...]}`.

For each vertex ``v`` we introduce three Boolean variables ``x_{v,1}``,
``x_{v,2}``, ``x_{v,3}`` meaning that vertex ``v`` receives colour 1, 2 or 3.
The mapping from ``(v, colour)`` to a SAT variable index is:

``var(v, c) = v * 3 + c``   (with ``v`` zero‑based and ``c`` in ``{1,2,3}``).

The CNF encodes the usual constraints:

1. **Each vertex gets at least one colour** – a clause ``(x_{v,1} ∨ x_{v,2} ∨ x_{v,3})``.
2. **Each vertex gets at most one colour** – for every pair of distinct colours
   ``c1, c2`` a clause ``(¬x_{v,c1} ∨ ¬x_{v,c2})``.
3. **Adjacent vertices cannot share a colour** – for every edge ``(u, v)`` and
   every colour ``c`` a clause ``(¬x_{u,c} ∨ ¬x_{v,c})``.

All clauses are added to the ``clauses`` list using the SAT literal encoding:
positive integers for the variable itself and negative integers for its negation.

The reduction runs in time polynomial in the size of the input graph (O(n + |E|)).
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of ``[u, v]``).

    Returns
    -------
    dict
        A SAT instance with keys ``"num_vars"`` and ``"clauses"``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Number of SAT variables: three per vertex.
    num_vars = n * 3
    clauses: List[List[int]] = []

    # Helper to map (vertex, colour) -> variable index (1‑based).
    def var(v: int, colour: int) -> int:
        # colour is 1,2,3
        return v * 3 + colour

    # 1. At least one colour per vertex.
    for v in range(n):
        clauses.append([var(v, 1), var(v, 2), var(v, 3)])

    # 2. At most one colour per vertex (pairwise mutual exclusion).
    for v in range(n):
        # (1,2), (1,3), (2,3)
        clauses.append([-var(v, 1), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 3)])
        clauses.append([-var(v, 2), -var(v, 3)])

    # 3. Adjacent vertices cannot share the same colour.
    for u, v in edges:
        for colour in (1, 2, 3):
            clauses.append([-var(u, colour), -var(v, colour)])

    return {"num_vars": num_vars, "clauses": clauses}

