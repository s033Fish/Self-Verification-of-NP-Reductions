"""Reduction from Hamiltonian Cycle to SAT.

The reduction follows the classic encoding using a variable x_{v,i} that is
true iff vertex ``v`` appears at position ``i`` in the Hamiltonian cycle.
We number variables from 1..n*n (where ``n`` is the number of vertices) in
row‑major order: ``var(v,i) = v * n + i + 1``.

The produced CNF enforces:

1. **Exactly one vertex per position** – each position gets at least one
   vertex and no two vertices can share the same position.
2. **Exactly one position per vertex** – each vertex appears somewhere in
   the cycle and cannot appear twice.
3. **Adjacency** – consecutive positions in the cycle must be connected by
   an edge of the input graph (including the wrap‑around from the last to
   the first position).

For graphs with ``n <= 2`` the Hamiltonian‑Cycle instance is always a NO‑
instance. We therefore output a trivially unsatisfiable SAT instance – a
single empty clause.

The function runs in polynomial time with respect to the size of the input
graph (O(n^3) clauses in the worst case) which satisfies the requirement.
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple, Set

from problems import HamiltonianCycle, Sat


def _var(v: int, i: int, n: int) -> int:
    """Map (vertex, position) to a SAT variable number (1‑based)."""
    return v * n + i + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dict adhering to :class:`HamiltonianCycle`'s format.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate source instance first.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge cases: n <= 2 are always NO. Return unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 1, "clauses": [[]]}  # empty clause -> unsat

    # Build adjacency set for O(1) edge queries.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))

    clauses: List[List[int]] = []
    num_vars = n * n

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var(v, i, n) for v in range(n)]
        clauses.append(clause)

    # 2. No position i contains two different vertices.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var(v, i, n), -_var(w, i, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var(v, i, n) for i in range(n)]
        clauses.append(clause)

    # 4. No vertex appears in two positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var(v, i, n), -_var(v, j, n)])

    # 5. Edge constraints: consecutive positions must be adjacent.
    # For each position i, forbid a pair (v,w) that is NOT an edge.
    for i in range(n):
        next_i = (i + 1) % n
        for v in range(n):
            for w in range(n):
                if (v, w) not in adj:
                    clauses.append([-_var(v, i, n), -_var(w, next_i, n)])

    return {"num_vars": num_vars, "clauses": clauses}

