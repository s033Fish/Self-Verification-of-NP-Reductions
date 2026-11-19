"""Reduction from Hamiltonian Cycle to SAT.

The source problem is an undirected graph G = (V, E) with |V| = n.
We create a CNF formula that is satisfiable iff G has a Hamiltonian
cycle. The classic encoding uses variables x_{i,v} meaning *vertex v is at
position i* of the cycle (positions are 0 … n‑1). The formula consists of

1. **Exactly‑one** vertex at each position.
2. **Exactly‑one** position for each vertex.
3. **Adjacency** constraints: consecutive positions must be connected by an
   edge of G (wrapping around from n‑1 back to 0).

All constraints are expressed as clauses of size 1, 2 or n. The number of
variables is n² (one for each pair (i, v)). The construction runs in
polynomial time.

Edge cases:
* For n <= 2 the source instance is always a NO instance. We return an
  unsatisfiable SAT instance – a formula with a single empty clause. The
  number of variables can be zero; an empty clause is unsatisfiable
  regardless of the variable count.
"""

from __future__ import annotations

from typing import Dict, List

# Import the problem classes to reuse validation helpers if needed.
from problems import HamiltonianCycle, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Map position ``i`` (0‑based) and vertex ``v`` (0‑based) to a SAT variable.

    Variables for SAT are 1‑based, so we add 1 to the zero‑based index.
    The total number of variables is ``n * n``.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    The returned dictionary follows the format required by the ``Sat`` class:
    ``{"num_vars": m, "clauses": [[lit, ...], ...]}`` where literals are
    signed integers.
    """
    # Validate the source instance first – this will raise if malformed.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case: n <= 2 -> always NO. Return an unsatisfiable formula.
    if n <= 2:
        # An empty clause makes the formula unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency set for quick look‑up of edges.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    clauses: List[List[int]] = []
    m = n * n  # total variables

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)
        # At most one vertex per position: pairwise mutual exclusion.
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(i, w, n)])

    # 2. Each vertex appears in exactly one position.
    for v in range(n):
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Non‑edge adjacency constraints.
    # For each position i and each unordered non‑edge {u, v}, forbid u at i
    # and v at i+1 (mod n), and vice‑versa.
    for i in range(n):
        next_i = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if not adj[u][v]:
                    # forbid (u at i) AND (v at next_i)
                    clauses.append([-_var_index(i, u, n), -_var_index(next_i, v, n)])
                    # also forbid the opposite direction
                    clauses.append([-_var_index(i, v, n), -_var_index(next_i, u, n)])

    # Return the SAT instance.
    sat_instance = {"num_vars": m, "clauses": clauses}
    # Validate the target instance to ensure correctness of the format.
    Sat.validate(sat_instance)
    return sat_instance

