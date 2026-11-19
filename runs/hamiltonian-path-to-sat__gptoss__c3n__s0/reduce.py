"""Reduction from Hamiltonian Path to SAT.

The reduction follows the classic encoding of Hamiltonian path existence as a
CNF formula.  For a graph with ``n`` vertices we introduce Boolean variables
``X_{i,v}`` (``i`` = position in the path, ``v`` = vertex) meaning *vertex v is
the i‑th vertex of the Hamiltonian path*.

Variable numbering (required by the SAT instance format) is:
    var_id = i * n + v + 1   # 1‑based

Constraints encoded as clauses:

1. **Each position contains at least one vertex** – a single clause per
   position with all ``X_{i,*}`` positive.
2. **Each position contains at most one vertex** – for every pair of distinct
   vertices ``v != w`` a clause ``¬X_{i,v} ∨ ¬X_{i,w}``.
3. **Each vertex appears in at least one position** – a single clause per
   vertex with all ``X_{*,v}`` positive.
4. **Each vertex appears in at most one position** – for every pair of distinct
   positions ``i != j`` a clause ``¬X_{i,v} ∨ ¬X_{j,v}``.
5. **Adjacency constraint** – for every consecutive pair of positions ``i``
   and ``i+1`` and for every *non‑edge* ``{v,w}`` we add ``¬X_{i,v} ∨ ¬X_{i+1,w}``.
   (Both orders are covered because the pair ``(v,w)`` and ``(w,v)`` are both
   considered when iterating over non‑edges.)

The reduction runs in polynomial time O(n^2 + n·|E̅|) where ``E̅`` is the set of
non‑edges.

Edge cases are handled explicitly:
* ``n == 0`` – the answer is always *no*.  We return a SAT instance with a
  single empty clause, which is unsatisfiable.
* ``n == 1`` – always *yes*.  We return a trivially satisfiable formula with
  zero variables and zero clauses.
* ``n == 2`` – the generic encoding already captures the required behaviour,
  but we keep the generic construction for simplicity.

The module defines a single public function ``reduce(instance)`` that takes a
HamiltonianPath instance (validated against ``HamiltonianPath.validate``) and
returns a SAT instance conforming to the format expected by ``Sat.validate``.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set

from problems import HamiltonianPath, Sat


def _var_id(i: int, v: int, n: int) -> int:
    """Map position ``i`` and vertex ``v`` to a SAT variable number (1‑based)."""
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a HamiltonianPath instance to an equivalent SAT instance.

    The returned instance is a dictionary ``{"num_vars": m, "clauses": [...]}``
    where ``m = n*n`` for ``n`` vertices (except for the trivial ``n=0`` case).
    """
    # Validate source instance first.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge‑case handling.
    if n == 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Trivially satisfiable: no variables, no clauses.
        return {"num_vars": 0, "clauses": []}

    # Build adjacency set for quick lookup.
    adj: Set[frozenset[int]] = {frozenset(edge) for edge in edges}

    num_vars = n * n
    clauses: List[List[int]] = []

    # 1. Each position has at least one vertex.
    for i in range(n):
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position has at most one vertex.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(i, w, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var_id(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex appears in at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # 5. Adjacency constraints for consecutive positions.
    # For each pair of positions i,i+1 and each non‑edge {v,w} add clause.
    for i in range(n - 1):
        for v in range(n):
            for w in range(n):
                if v == w:
                    continue
                if frozenset((v, w)) not in adj:
                    # Not an edge, forbid consecutive placement.
                    clauses.append([-_var_id(i, v, n), -_var_id(i + 1, w, n)])

    return {"num_vars": num_vars, "clauses": clauses}

