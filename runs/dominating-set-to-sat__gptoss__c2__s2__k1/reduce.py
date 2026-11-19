"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem (Sat) instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are integers: +v for true, -v for false, with variables 1..m.

The reduction creates a Boolean variable x_i for each vertex i (1‑based).
Clause (x_v ∨ x_u1 ∨ ... ) ensures each vertex is dominated.
An at‑most‑k cardinality constraint on the x_i variables is added using
the sequential counter encoding of Sinz (2005), which introduces O(n·k)
auxiliary variables s_{i,j}.
Edge cases are handled explicitly.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    n = instance.get("n", 0)
    edges = instance.get("edges", [])
    k = instance.get("k", 0)

    # Edge cases
    if k < 0:
        # Unsatisfiable formula: single empty clause
        return {"num_vars": 0, "clauses": [[]]}
    if n == 0:
        # Empty graph is always dominated (yes). Empty formula is satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        # Trivially yes – any set of at most n vertices works.
        return {"num_vars": 0, "clauses": []}

    # Build adjacency list
    adj: List[set] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    clauses: List[List[int]] = []

    # Dominating constraints: each vertex v must be in D or adjacent to a vertex in D
    for v in range(n):
        lits = [v + 1]  # x_v (variables are 1‑based)
        for u in adj[v]:
            lits.append(u + 1)
        clauses.append(lits)

    # Cardinality (at‑most‑k) constraints using sequential counter encoding
    if k == 0:
        # Force all x_i to be false
        for i in range(1, n + 1):
            clauses.append([ -i ])
        num_vars = n
        return {"num_vars": num_vars, "clauses": clauses}

    # Helper to map auxiliary variable s_{i,j} to a SAT variable number.
    # i in 1..n, j in 1..k
    def aux(i: int, j: int) -> int:
        return n + (i - 1) * k + j

    # 1) (¬x_i ∨ s_{i,1}) for each i
    for i in range(1, n + 1):
        clauses.append([ -i, aux(i, 1) ])

    # 2) (¬s_{i‑1,j} ∨ s_{i,j}) for i ≥ 2, 1 ≤ j ≤ k
    for i in range(2, n + 1):
        for j in range(1, k + 1):
            clauses.append([ -aux(i - 1, j), aux(i, j) ])

    # 3) (¬x_i ∨ ¬s_{i‑1,j‑1} ∨ s_{i,j}) for i ≥ 2, 2 ≤ j ≤ k
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            clauses.append([ -i, -aux(i - 1, j - 1), aux(i, j) ])

    # 4) (¬x_i ∨ ¬s_{i‑1,k}) for i ≥ 2 – prevents > k true variables
    for i in range(2, n + 1):
        clauses.append([ -i, -aux(i - 1, k) ])

    num_vars = n + n * k
    return {"num_vars": num_vars, "clauses": clauses}


# Export the reduce function for external use
__all__ = ["reduce"]

