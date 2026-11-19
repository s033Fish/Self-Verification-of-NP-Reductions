"""Reduction from Hamiltonian Cycle to SAT.

The reduction follows the classic encoding using variables x_{i,v} that are
true iff vertex ``v`` appears at position ``i`` in the Hamiltonian cycle.
Positions are numbered 0..n-1 and vertices 0..n-1.  The variable index in the
SAT instance is ``i * n + v + 1`` (SAT variables start at 1).

Constraints (all expressed as CNF clauses):
1. **Each position contains at least one vertex** – a clause with all
   variables for that position.
2. **Each position contains at most one vertex** – for every distinct pair
   of vertices (u, v) a clause ``¬x_{i,u} ∨ ¬x_{i,v}``.
3. **Each vertex appears in at least one position** – a clause with all
   variables for that vertex across positions.
4. **Each vertex appears in at most one position** – for every distinct pair
   of positions (i, j) a clause ``¬x_{i,v} ∨ ¬x_{j,v}``.
5. **Non‑edges cannot be consecutive in the cycle** – for every unordered
   non‑edge {u, v} and every position i, add clauses
   ``¬x_{i,u} ∨ ¬x_{(i+1) mod n, v}`` and ``¬x_{i,v} ∨ ¬x_{(i+1) mod n, u}``.

Edge cases:
* For ``n <= 2`` a Hamiltonian cycle cannot exist.  We therefore return a
  SAT instance that is unsatisfiable – a single empty clause ``[]``.

The function runs in polynomial time in the size of the graph (O(n^3) in the
worst case) which satisfies the requirement.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import HamiltonianCycle, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``i`` and vertex ``v``.

    SAT variables are 1‑based, so we add 1.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to an equivalent SAT instance.

    The returned instance is a dict compatible with :class:`Sat` – it has the
    keys ``"num_vars"`` and ``"clauses"``.
    """
    # Validate source instance first.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case: n <= 2 → always NO. Return an unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for quick lookup.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    num_vars = n * n
    clauses: List[List[int]] = []

    # 1. Each position has at least one vertex.
    for i in range(n):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position has at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var_index(i, u, n), -_var_index(i, v, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex appears in at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 5. Non‑edges cannot be consecutive.
    for u in range(n):
        for v in range(u + 1, n):
            if not adj[u][v]:
                for i in range(n):
                    nxt = (i + 1) % n
                    # u at i and v at i+1 is forbidden
                    clauses.append([-_var_index(i, u, n), -_var_index(nxt, v, n)])
                    # v at i and u at i+1 is forbidden
                    clauses.append([-_var_index(i, v, n), -_var_index(nxt, u, n)])

    return {"num_vars": num_vars, "clauses": clauses}

