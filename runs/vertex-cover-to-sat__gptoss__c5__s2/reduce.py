"""Reduction from Vertex Cover to SAT.

The reduction creates a SAT formula that is satisfiable exactly when the
given graph has a vertex cover of size at most ``k``.

Encoding:
  * For each vertex ``i`` (0‑based) and each position ``j`` in a cover of
    size ``k`` we introduce a Boolean variable ``x_{i,j}`` that is true iff
    vertex ``i`` occupies position ``j`` in the cover.
  * The total number of variables is ``n * k`` (or ``0`` when ``k <= 0``).
  * Constraints are added as clauses:
    - **Edge coverage**: for every edge ``(u, v)`` the clause
      ``x_{u,1} ∨ … ∨ x_{u,k} ∨ x_{v,1} ∨ … ∨ x_{v,k}`` guarantees that at
      least one endpoint of the edge is selected in some position.
    - **At most one position per vertex**: for each vertex ``i`` and each
      pair of distinct positions ``j1 < j2`` we add the clause
      ``¬x_{i,j1} ∨ ¬x_{i,j2}``.
    - **At most one vertex per position**: for each position ``j`` and each
      pair of distinct vertices ``i1 < i2`` we add the clause
      ``¬x_{i1,j} ∨ ¬x_{i2,j}``.

The construction works for all edge cases:
  * ``k < 0`` – we output an unsatisfiable formula (a single empty clause).
  * ``k >= n`` – the constraints are still correct; the formula is always
    satisfiable because we can place each vertex in a distinct position.
  * Graph with no edges – the edge‑coverage clause list is empty, so the
    resulting CNF has no clauses and is trivially satisfiable.

The reduction runs in polynomial time w.r.t. the size of the input graph.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, Sat


def _var_index(i: int, j: int, k: int) -> int:
    """Map vertex ``i`` and position ``j`` to a SAT variable number.

    Variables are numbered starting from ``1`` as required by the SAT
    definition. ``k`` is the total number of positions (the cover size).
    """
    return i * k + j + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``VertexCover`` format.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the source instance first.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge case: k < 0 – always unsatisfiable.
    if k < 0:
        # A formula with a single empty clause is unsatisfiable.
        return {"num_vars": 1, "clauses": [[]]}

    # When k == 0, the only possible cover is the empty set.
    # The reduction below will create zero variables and only edge clauses.
    # If there is any edge, those clauses will be empty (unsat). If there are
    # no edges, the formula will have no clauses (sat). This matches the
    # definition, so we can handle k == 0 with the general construction.

    total_vars = n * k
    clauses: List[List[int]] = []

    # 1. Edge coverage clauses.
    for u, v in edges:
        clause: List[int] = []
        for j in range(k):
            # Add positive literals for both endpoints in each position.
            clause.append(_var_index(u, j, k))
            clause.append(_var_index(v, j, k))
        clauses.append(clause)

    # 2. At most one position per vertex.
    for i in range(n):
        for j1 in range(k):
            for j2 in range(j1 + 1, k):
                clauses.append([-_var_index(i, j1, k), -_var_index(i, j2, k)])

    # 3. At most one vertex per position.
    for j in range(k):
        for i1 in range(n):
            for i2 in range(i1 + 1, n):
                clauses.append([-_var_index(i1, j, k), -_var_index(i2, j, k)])

    return {"num_vars": total_vars, "clauses": clauses}

