"""Reduction from Vertex Cover to SAT.

The source problem is :class:`VertexCover` defined in ``problems.py``.
The target problem is :class:`Sat` defined in the same file.

The reduction follows the classic polynomial‑time construction using
``k`` position variables.  For a graph with ``n`` vertices and a bound
``k`` we create boolean variables ``x_{i,p}`` meaning *vertex i is placed
in position p* (``0 <= i < n`` and ``0 <= p < k``).  The formula consists
of three families of clauses:

1. **Each position is occupied** – for every position ``p`` we add a clause
   ``(x_{0,p} ∨ x_{1,p} ∨ … ∨ x_{n‑1,p})``.
2. **At most one vertex per position** – for each position ``p`` and any
   two distinct vertices ``i < j`` we add ``(¬x_{i,p} ∨ ¬x_{j,p})``.
3. **No vertex appears in two different positions** – for each vertex
   ``i`` and any two distinct positions ``p < q`` we add ``(¬x_{i,p} ∨ ¬x_{i,q})``.
4. **Every edge is covered** – for each edge ``(u, v)`` we add a clause
   ``(x_{u,0} ∨ x_{v,0} ∨ x_{u,1} ∨ x_{v,1} ∨ … ∨ x_{u,k‑1} ∨ x_{v,k‑1})``.

The construction is polynomial in ``n`` and ``k`` (the number of
variables is ``n·k`` and the number of clauses is ``k + n·C(k,2) + n·C(n,2) + |E|·k``).

Edge cases are handled explicitly:

* ``k < 0`` – the answer is always *no*.  We return an unsatisfiable
  formula consisting of a single empty clause ``[]``.
* ``k >= n`` – the answer is always *yes*.  We return a trivially
  satisfiable formula with no clauses.

Both the input and output are validated using the ``validate`` methods
from ``problems.py``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, Sat


def _var_index(i: int, p: int, k: int) -> int:
    """Return the SAT variable number for vertex ``i`` in position ``p``.

    SAT variables are numbered starting from 1.  The mapping is
    ``idx = i * k + p + 1``.
    """
    return i * k + p + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an equivalent SAT instance.

    The returned instance is a dict matching the format required by
    :class:`Sat` – ``{"num_vars": m, "clauses": [[...], ...]}``.
    """
    # Validate source instance
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases
    if k < 0:
        # Unsatisfiable formula: a single empty clause
        sat_instance = {"num_vars": 1, "clauses": [[]]}
        Sat.validate(sat_instance)
        return sat_instance
    if k >= n:
        # Trivially satisfiable (no clauses needed)
        sat_instance = {"num_vars": 0, "clauses": []}
        Sat.validate(sat_instance)
        return sat_instance

    clauses: List[List[int]] = []

    # 1. Each position must be occupied by at least one vertex (at‑least‑one)
    for p in range(k):
        clause = [_var_index(i, p, k) for i in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position (pairwise mutual exclusion)
    for p in range(k):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, p, k), -_var_index(j, p, k)])

    # 3. No vertex may appear in two different positions (at most once overall)
    for i in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-_var_index(i, p, k), -_var_index(i, q, k)])

    # 4. Edge coverage clauses
    for u, v in edges:
        clause = []
        for p in range(k):
            clause.append(_var_index(u, p, k))
            clause.append(_var_index(v, p, k))
        clauses.append(clause)

    sat_instance = {"num_vars": n * k, "clauses": clauses}
    Sat.validate(sat_instance)
    return sat_instance

