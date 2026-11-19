"""Reduction from Vertex Cover to SAT.

The source problem is :class:`VertexCover` (see ``problems.py``) with an
instance ``{"n": n, "edges": [[u, v], ...], "k": k}``.
The target problem is :class:`Sat` with an instance ``{"num_vars": m,
"clauses": [[literal, ...], ...]}``.

We use the classic polynomial‑time reduction that introduces a Boolean
variable ``x_{i,j}`` meaning *vertex i is the j‑th vertex of the cover*.
The reduction works for ``0 <= k < n``.  Edge cases are handled
separately:

* ``k < 0`` – the answer is always *no*.  We return a formula that is
  unsatisfiable (a single empty clause).
* ``k == 0`` – the formula has ``0`` variables and contains an empty
  clause for every edge.  It is satisfiable iff the graph has no edges.
* ``k >= n`` – the answer is always *yes*.  We return an empty formula
  (no clauses, ``0`` variables), which is trivially satisfiable.

For the main case ``0 < k < n`` we create the following CNF:

1. *Exactly one vertex per position* – for each position ``j`` (1‑based)
   we add a clause that at least one vertex occupies it and pairwise
   clauses that forbid two different vertices from sharing the same
   position.
2. *At most one position per vertex* – for each vertex ``i`` we add
   pairwise clauses forbidding it from appearing in two different
   positions.
3. *Edge coverage* – for each edge ``(u, v)`` we add a clause that at
   least one of its endpoints appears in some position.

The total number of variables is ``n * k`` and the number of clauses is
polynomial in ``n, m, k`` (specifically ``O(n*k + m*k)``), satisfying the
requirement for a polynomial‑time reduction.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, Sat


def _var_index(i: int, j: int, k: int) -> int:
    """Return the SAT variable number for vertex ``i`` at position ``j``.

    Variables are numbered from 1.  ``i`` is 0‑based vertex index, ``j`` is
    1‑based position (1..k).  ``k`` is the total number of positions.
    """
    return i * k + j


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a SAT instance.

    The returned dictionary conforms to the format required by the
    ``Sat`` class in ``problems.py``.
    """
    # Validate the source instance (may raise InvalidInstance).
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases according to the specification of VertexCover.
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if k == 0:
        # No variables. Each edge forces an empty clause (unsat if any edge).
        clauses: List[List[int]] = []
        for _ in edges:
            clauses.append([])  # empty clause = unsatisfiable
        return {"num_vars": 0, "clauses": clauses}
    if k >= n:
        # Trivially satisfiable – empty formula.
        return {"num_vars": 0, "clauses": []}

    # Main reduction for 0 < k < n.
    num_vars = n * k
    clauses: List[List[int]] = []

    # 1. At least one vertex per position j.
    for j in range(1, k + 1):
        clause = [_var_index(i, j, k) for i in range(n)]
        clauses.append(clause)

    # 2. No two vertices share the same position (at most one per position).
    for j in range(1, k + 1):
        for i1 in range(n):
            for i2 in range(i1 + 1, n):
                clauses.append([-_var_index(i1, j, k), -_var_index(i2, j, k)])

    # 3. No vertex appears in two different positions.
    for i in range(n):
        for j1 in range(1, k + 1):
            for j2 in range(j1 + 1, k + 1):
                clauses.append([-_var_index(i, j1, k), -_var_index(i, j2, k)])

    # 4. Edge coverage clauses.
    for u, v in edges:
        clause: List[int] = []
        for j in range(1, k + 1):
            clause.append(_var_index(u, j, k))
            clause.append(_var_index(v, j, k))
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

