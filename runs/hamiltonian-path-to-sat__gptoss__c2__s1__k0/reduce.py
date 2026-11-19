"""Reduction from Hamiltonian Path (undirected) to SAT (CNF).

The source problem instance is a dictionary with keys "n" and "edges" as described in ``problems.py``. The target SAT instance follows the same format used by the ``Sat`` class – a ``num_vars`` field and a list of clauses, each clause being a list of integer literals.

The classic polynomial‑time reduction introduces a Boolean variable ``x_{i,v}`` that is true exactly when vertex ``v`` occupies position ``i`` in a Hamiltonian path (positions are ``0 .. n‑1``). There are ``n*n`` such variables, numbered from ``1`` to ``n*n`` in row‑major order:

    var(i, v) = i * n + v + 1   (0‑based i and v)

The CNF encodes the following constraints:

1. **Every position is occupied** – for each position ``i`` a clause that
   contains all ``x_{i,v}`` for ``v`` in ``0..n-1``.
2. **Positions hold at most one vertex** – for each ``i`` and each pair of
   distinct vertices ``v<w`` a clause ``¬x_{i,v} ∨ ¬x_{i,w}``.
3. **Every vertex appears somewhere** – for each vertex ``v`` a clause that
   contains all ``x_{i,v}`` for ``i`` in ``0..n-1``.
4. **Vertices appear at most once** – for each ``v`` and each pair of
   distinct positions ``i<j`` a clause ``¬x_{i,v} ∨ ¬x_{j,v}``.
5. **Adjacency requirement** – for every consecutive pair of positions
   ``i, i+1`` and for every ordered pair of vertices ``(u, v)`` that is **not**
   an edge of the input graph, we add ``¬x_{i,u} ∨ ¬x_{i+1,v}``.  This forbids
   using a non‑edge between consecutive vertices of the path.

Edge cases:
* ``n == 0`` – the Hamiltonian‑Path instance is a definite *no*; we return an
  unsatisfiable SAT formula consisting of a single empty clause.
* ``n == 1`` – the construction above yields a trivially satisfiable formula.

The reduction runs in polynomial time (O(n⁴) in the worst case, well within
the allowed limits for the benchmark).
"""

from __future__ import annotations

from typing import List, Dict, Any, Set, FrozenSet


def _var_id(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for ``x_{i,v}``.

    Variables are 1‑based as required by the SAT format.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    Parameters
    ----------
    instance:
        ``{"n": int, "edges": [[u, v], ...]}`` – exactly the format used by
        ``HamiltonianPath`` in ``problems.py``.

    Returns
    -------
    dict
        ``{"num_vars": m, "clauses": [[lit, ...], ...]}`` compatible with the
        ``Sat`` problem class.
    """
    n = instance.get("n")
    edges = instance.get("edges", [])

    # Edge case n == 0 → unsatisfiable formula (empty clause).
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Build a set of existing undirected edges for O(1) membership tests.
    edge_set: Set[FrozenSet[int]] = {frozenset((u, v)) for u, v in edges}

    m = n * n  # total number of variables
    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position i has at most one vertex.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(i, w, n)])

    # 3. Every vertex appears in some position.
    for v in range(n):
        clause = [_var_id(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # 5. Adjacent positions must correspond to an edge.
    # For every ordered pair (u, v) that is not an edge, forbid it.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edge_set:
                    clauses.append([-_var_id(i, u, n), -_var_id(i + 1, v, n)])

    return {"num_vars": m, "clauses": clauses}

