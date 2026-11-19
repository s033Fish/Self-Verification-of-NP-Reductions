"""Reduction from Hamiltonian Path to SAT.

The source problem is :class:`HamiltonianPath` (undirected graph, any
endpoints).  The target is :class:`Sat` – a generic CNF formula with
variables numbered from ``1`` to ``m``.

We use the classic encoding with variables ``x_{i,v}`` meaning *vertex* ``v``
appears at *position* ``i`` in the Hamiltonian path (positions are 0‑based
here, but the encoding is independent of the chosen indexing).  The
constraints are:

1. **Each position holds at least one vertex** – a clause containing all
   ``x_{i,v}`` for a fixed ``i``.
2. **No position holds two vertices** – for each ``i`` and distinct ``v,w``
   a binary clause ``¬x_{i,v} ∨ ¬x_{i,w}``.
3. **Each vertex appears somewhere** – a clause containing all ``x_{i,v}``
   for a fixed ``v``.
4. **No vertex appears twice** – for each ``v`` and distinct ``i,j`` a
   binary clause ``¬x_{i,v} ∨ ¬x_{j,v}``.
5. **Consecutive vertices must be adjacent** – for every non‑edge ``{u,v}``
   and every position ``i`` we forbid the assignment ``x_{i,u}`` and
   ``x_{i+1,v}`` (and symmetrically ``x_{i,v}`` with ``x_{i+1,u}``).

The number of variables is ``n * n`` (``n`` positions × ``n`` vertices).
All clauses are generated in polynomial time.

Edge cases:
* ``n == 0`` – the source instance is a definite *no*.  We output a SAT
  instance with ``num_vars = 0`` and a single empty clause ``[]`` which is
  unsatisfiable.
* ``n == 1`` – the source instance is always *yes*.  The generic encoding
  works and yields a satisfiable formula, but for simplicity we output a
  trivially satisfiable formula with ``num_vars = 0`` and no clauses.

The function ``reduce`` follows the required signature and does not call any
solver; it merely builds the CNF.
"""

from __future__ import annotations

from typing import List, Dict

from problems import HamiltonianPath, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Map position ``i`` (0‑based) and vertex ``v`` to a SAT variable.

    Variables are numbered from 1 to ``n*n``.  The exact mapping is not
    important as long as it is bijective.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary matching the format described in the docstring of
        :class:`HamiltonianPath` – ``{"n": n, "edges": [[u, v], ...]}``.

    Returns
    -------
    dict
        A SAT instance ``{"num_vars": m, "clauses": [...]}`` such that the
        SAT instance is satisfiable iff the original graph has a Hamiltonian
        path.
    """
    # Validate using the source class – this raises InvalidInstance if the
    # input is malformed, matching the contract of the reduction.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case handling ---------------------------------------------------
    if n == 0:
        # Unsatisfiable formula: empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Trivially satisfiable – no variables, no clauses.
        return {"num_vars": 0, "clauses": []}

    # Build adjacency matrix for quick lookup of existing edges.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    m = n * n  # total variables
    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position i has at most one vertex.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(i, w, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 5. Consecutive positions must correspond to an edge.
    # For every pair of vertices that are NOT adjacent, forbid them to be
    # consecutive in either order.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if not adj[u][v]:
                    clauses.append([-_var_index(i, u, n), -_var_index(i + 1, v, n)])
    # The loop above already adds both (u,v) and (v,u) when they are
    # non‑edges, so we do not need a separate symmetric pass.

    return {"num_vars": m, "clauses": clauses}

