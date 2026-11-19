"""Reduction from Vertex Cover to SAT.

The reduction follows the classic polynomial‑time construction that uses
"position" variables.  For a graph with ``n`` vertices and a target cover size
``k`` we introduce a Boolean variable ``x_{i,j}`` meaning *vertex i is placed in
position j of the cover* (1 ≤ j ≤ k).  To allow covers of size **at most** k we
add one extra dummy vertex (index ``n``) that may occupy any unused position –
the dummy never participates in edge‑cover clauses.

Variables are numbered consecutively from 1 to ``m = (n + 1) * k``.  The CNF
contains four families of clauses:

1. **Every position is occupied** – for each j, the clause
   ``x_{0,j} ∨ x_{1,j} ∨ … ∨ x_{n,j}``.
2. **A vertex appears in at most one position** – for each vertex i and
   each pair j < l, the clause ``¬x_{i,j} ∨ ¬x_{i,l}``.
3. **A position holds at most one vertex** – for each position j and each
   pair i < l, the clause ``¬x_{i,j} ∨ ¬x_{l,j}``.
4. **Every edge is covered** – for each edge (u, v) the clause
   ``x_{u,1} ∨ … ∨ x_{u,k} ∨ x_{v,1} ∨ … ∨ x_{v,k}``.

The construction is polynomial in ``n`` and ``k``.  Edge cases are handled
directly:

* ``k < 0`` – always unsatisfiable (return a formula containing an empty
  clause).
* ``k >= n`` – always satisfiable (return an empty formula).
* No edges – trivially satisfiable.
* ``k == 0`` with edges – unsatisfiable.

The function ``reduce`` validates the input instance, builds the CNF as
described, and returns it as a dictionary compatible with the ``Sat`` problem
definition.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, Sat


def _var_id(i: int, j: int, k: int) -> int:
    """Map vertex index ``i`` (0‑based, including dummy) and position ``j``
    (1‑based) to a SAT variable number.

    Variables are numbered from 1 upwards.
    """
    return i * k + j


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an equivalent SAT instance.

    The returned instance satisfies the ``Sat`` format:
    ``{"num_vars": m, "clauses": [[lit, ...], ...]}``.
    """
    # Validate source instance.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases handled directly.
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}
    if k >= n:
        # Always satisfiable – empty formula.
        return {"num_vars": 0, "clauses": []}
    if not edges:
        return {"num_vars": 0, "clauses": []}
    if k == 0:
        # No vertices may be chosen but there is at least one edge.
        return {"num_vars": 1, "clauses": [[]]}

    # General case.
    total_vertices = n + 1  # extra dummy vertex at index n
    m = total_vertices * k
    clauses: List[List[int]] = []

    # 1. Every position j must be occupied by some vertex (including dummy).
    for j in range(1, k + 1):
        clause = [_var_id(i, j, k) for i in range(total_vertices)]
        clauses.append(clause)

    # 2. A vertex cannot appear in two different positions.
    for i in range(total_vertices):
        for j1 in range(1, k + 1):
            for j2 in range(j1 + 1, k + 1):
                clauses.append([-_var_id(i, j1, k), -_var_id(i, j2, k)])

    # 3. A position cannot be occupied by two different vertices.
    for j in range(1, k + 1):
        for i1 in range(total_vertices):
            for i2 in range(i1 + 1, total_vertices):
                clauses.append([-_var_id(i1, j, k), -_var_id(i2, j, k)])

    # 4. Edge coverage clauses.
    for u, v in edges:
        clause = []
        for j in range(1, k + 1):
            clause.append(_var_id(u, j, k))
            clause.append(_var_id(v, j, k))
        clauses.append(clause)

    # Validate the produced SAT instance before returning.
    Sat.validate({"num_vars": m, "clauses": clauses})
    return {"num_vars": m, "clauses": clauses}

