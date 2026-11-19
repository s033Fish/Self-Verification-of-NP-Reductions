"""Reduction from Hamiltonian Path to SAT.

The source problem is :class:`HamiltonianPath` (undirected graph, any
endpoints).  The target problem is :class:`Sat` (general CNF SAT).

For a graph with ``n`` vertices we introduce Boolean variables
``x_{i,v}`` (``i`` = position in the path, ``v`` = vertex).  Variable
``x_{i,v}`` is true iff vertex ``v`` occupies position ``i`` of the
Hamiltonian path.

Constraints (encoded as CNF clauses):

1. **Each position contains exactly one vertex** – a clause with all
   ``x_{i,*}`` (at least one) plus binary clauses ``¬x_{i,u} ∨ ¬x_{i,v}``
   for all ``u != v`` (at most one).
2. **Each vertex appears exactly once** – analogous to (1) but over the
   positions for a fixed vertex.
3. **Consecutive vertices must be adjacent** – for every non‑edge ``{u,v}``
   and every consecutive position pair ``i,i+1`` we forbid the ordering
   ``u`` then ``v`` and also ``v`` then ``u`` with clauses
   ``¬x_{i,u} ∨ ¬x_{i+1,v}`` and ``¬x_{i,v} ∨ ¬x_{i+1,u}``.

The reduction runs in polynomial time (``O(n^3)`` clauses, ``n^2`` variables).

Edge cases:
* ``n = 0`` – the answer is always *no*.  We return an unsatisfiable
  formula consisting of a single empty clause.
* ``n = 1`` – always *yes*.  We return a trivially satisfiable formula
  (one variable that is forced true).

The function ``reduce`` validates the input, builds the CNF, and returns it
in the format expected by :class:`Sat`.
"""

from __future__ import annotations

from typing import List, Dict

from problems import HamiltonianPath, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Map position ``i`` and vertex ``v`` (both 0‑based) to a SAT variable.

    Variables for SAT are 1‑based, so we add 1 after the linearisation.
    The total number of variables is ``n * n``.
    """

    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    The returned dictionary follows the format required by ``Sat``:
    ``{"num_vars": m, "clauses": [[l1, l2, ...], ...]}``.
    """

    # Validate the source instance using the provided class.
    HamiltonianPath.validate(instance)
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge set for O(1) adjacency queries.
    adj = {frozenset(e) for e in edges}

    # Special cases for n = 0 and n = 1.
    if n == 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Satisfiable formula: one variable forced true.
        return {"num_vars": 1, "clauses": [[1]]}

    m = n * n
    clauses: List[List[int]] = []

    # 1. Each position i has exactly one vertex.
    for i in range(n):
        # At least one vertex.
        clauses.append([_var_index(i, v, n) for v in range(n)])
        # At most one vertex.
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-
                    _var_index(i, u, n), -_var_index(i, v, n)])

    # 2. Each vertex v appears in exactly one position.
    for v in range(n):
        # At least one position.
        clauses.append([_var_index(i, v, n) for i in range(n)])
        # At most one position.
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-
                    _var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Edge constraints for consecutive positions.
    # Pre‑compute all unordered non‑edges.
    non_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in adj:
                non_edges.append((u, v))

    for i in range(n - 1):
        for (u, v) in non_edges:
            # forbid u at i and v at i+1
            clauses.append([-
                _var_index(i, u, n), -_var_index(i + 1, v, n)])
            # forbid v at i and u at i+1 (graph is undirected)
            clauses.append([-
                _var_index(i, v, n), -_var_index(i + 1, u, n)])

    return {"num_vars": m, "clauses": clauses}

