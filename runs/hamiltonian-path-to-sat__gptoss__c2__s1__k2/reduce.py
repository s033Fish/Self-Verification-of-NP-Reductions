"""Reduction from Hamiltonian Path to SAT.

The source problem is an undirected Hamiltonian Path instance:
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1.  The target problem is SAT in CNF:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are represented as integers: a positive integer +v means variable v
is true, a negative integer -v means variable v is false.  Variables are
1‑based.

The classic polynomial‑time reduction introduces a boolean variable
``x_{i,v}`` that is true exactly when vertex ``v`` occupies position ``i``
in the Hamiltonian path (positions are 0‑based).  There are ``n * n`` such
variables which we number consecutively as ``var(i, v) = i * n + v + 1``.

Constraints encoded as CNF clauses:

1. **Each position contains at least one vertex** – a clause with all
   ``x_{i,v}`` for a fixed ``i``.
2. **Each position contains at most one vertex** – for every pair ``v≠w``
   a clause ``¬x_{i,v} ∨ ¬x_{i,w}``.
3. **Each vertex appears in at least one position** – a clause with all
   ``x_{i,v}`` for a fixed ``v``.
4. **Each vertex appears in at most one position** – for every pair
   ``i≠j`` a clause ``¬x_{i,v} ∨ ¬x_{j,v}``.
5. **Consecutive vertices must be adjacent** – for every non‑edge ``(v,w)``
   and every position ``i`` (0 ≤ i < n‑1) we add ``¬x_{i,v} ∨ ¬x_{i+1,w}``.
   The ordered pair loop naturally adds both directions, handling the
   undirected nature of the graph.

Edge cases:
* ``n == 0`` – the Hamiltonian‑Path instance is a definite **NO**.  We
  return a SAT instance with a single empty clause (unsatisfiable).
* ``n == 1`` – always **YES**.  The construction above yields a trivially
  satisfiable formula (unit clauses only).

The reduction runs in ``O(n³)`` time and produces ``O(n³)`` clauses, which
is polynomial in the size of the input.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set, Tuple

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        two‑element lists).  The format follows the description in the
        problem statement.

    Returns
    -------
    dict
        A SAT instance in the format ``{"num_vars": m, "clauses": [...]}``.
    """

    n: int = int(instance.get("n", 0))
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case n == 0 : always unsatisfiable.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Helper to map (position, vertex) -> SAT variable (1‑based).
    def var(i: int, v: int) -> int:
        return i * n + v + 1

    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clauses.append([var(i, v) for v in range(n)])

    # 2. Each position i has at most one vertex.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(i, v), -var(i, w)])

    # 3. Each vertex v appears in at least one position.
    for v in range(n):
        clauses.append([var(i, v) for i in range(n)])

    # 4. Each vertex v appears in at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, v), -var(j, v)])

    # Build a set of existing undirected edges for O(1) adjacency checks.
    edge_set: Set[Tuple[int, int]] = set()
    for u, w in edges:
        edge_set.add((u, w))
        edge_set.add((w, u))

    # 5. Consecutive positions must correspond to an edge.
    # For every ordered pair (v, w) that is NOT an edge, forbid v at i and w at i+1.
    for i in range(n - 1):
        for v in range(n):
            for w in range(n):
                if v == w:
                    continue
                if (v, w) not in edge_set:
                    clauses.append([-var(i, v), -var(i + 1, w)])

    num_vars = n * n
    return {"num_vars": num_vars, "clauses": clauses}

