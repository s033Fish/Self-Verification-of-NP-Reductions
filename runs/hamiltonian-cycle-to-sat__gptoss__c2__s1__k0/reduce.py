"""Reduction from Hamiltonian Cycle (undirected) to SAT (CNF).

The source problem instance is a dictionary with keys:
    - "n": number of vertices (vertices are 0..n-1)
    - "edges": list of [u, v] undirected edges (u != v)

The target SAT instance format is a dictionary with keys:
    - "num_vars": total number of Boolean variables (1-indexed)
    - "clauses": list of clauses, each clause is a list of literals.
      A literal is an integer: +v for variable v being True, -v for False.

The reduction follows the classic textbook construction using variables
``x_{v,i}`` meaning "vertex v appears at position i in the Hamiltonian
cycle" (positions are 0..n-1).  The formula enforces:

1. Each position is occupied by exactly one vertex.
2. Each vertex occupies exactly one position.
3. Consecutive positions correspond to edges of the graph.
4. To break symmetry we fix vertex 0 at position 0 (this also handles the
   case n <= 2 by producing an unsatisfiable formula).

The construction runs in polynomial time O(n^2 + n*|non‑edges|) and the
generated SAT instance is satisfiable iff the original graph has a Hamiltonian
cycle.
"""

from typing import List, Dict, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian Cycle instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        {"n": int, "edges": [[u, v], ...]}

    Returns
    -------
    dict
        {"num_vars": m, "clauses": [[lit, ...], ...]}
    """

    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]

    # Edge cases: n <= 2 never has a Hamiltonian cycle.
    if n <= 2:
        # Return an unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for O(1) edge lookup.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    # Helper to map (v, i) -> variable number (1‑based).
    def var(v: int, i: int) -> int:
        return v * n + i + 1

    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [var(v, i) for v in range(n)]
        clauses.append(clause)

    # 1b. No two vertices occupy the same position.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(v, i), -var(w, i)])

    # 2. Each vertex appears in at least one position.
    for v in range(n):
        clause = [var(v, i) for i in range(n)]
        clauses.append(clause)

    # 2b. No vertex appears in two different positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 3. Edge constraints: if (u, v) is NOT an edge, they cannot be consecutive.
    # For each non‑edge and each position i, forbid u at i and v at i+1 (mod n).
    for u in range(n):
        for v in range(u + 1, n):
            if not adj[u][v]:
                for i in range(n):
                    j = (i + 1) % n
                    clauses.append([-var(u, i), -var(v, j)])
                    clauses.append([-var(v, i), -var(u, j)])

    # 4. Fix vertex 0 at position 0 to break symmetry.
    #   - x_{0,0} must be true.
    clauses.append([var(0, 0)])
    #   - vertex 0 cannot appear elsewhere.
    for i in range(1, n):
        clauses.append([-var(0, i)])
    #   - no other vertex can be at position 0.
    for v in range(1, n):
        clauses.append([-var(v, 0)])

    num_vars = n * n
    return {"num_vars": num_vars, "clauses": clauses}

