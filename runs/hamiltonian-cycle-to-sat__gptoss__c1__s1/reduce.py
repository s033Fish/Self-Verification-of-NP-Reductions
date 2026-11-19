"""Reduction from Hamiltonian Cycle to SAT.

Given an undirected graph G = (V, E) with |V| = n, we create a CNF
formula that is satisfiable iff G has a Hamiltonian cycle.

Variables:
    x_{i,v}  (i = 0..n-1, v = 0..n-1)
    meaning "vertex v is the i‑th vertex in the cycle".
    We number variables from 1 to n*n using index = i*n + v + 1.

Clauses encode:
  1. Every position i is occupied by at least one vertex.
  2. No position i contains two different vertices.
  3. Every vertex appears in at least one position.
  4. No vertex appears in two different positions.
  5. Consecutive vertices must be adjacent in G (including the wrap‑around
     from position n-1 to 0). For each non‑edge {u,v} we forbid the pair
     (u at i, v at i+1) and (v at i, u at i+1).

Edge cases:
  * For n <= 2 the Hamiltonian cycle problem is always a NO instance.
    We therefore output an unsatisfiable formula (a single empty clause).

The function ``reduce`` receives an instance of the source problem (as
specified in ``problems.py``) and returns an instance of the target SAT
problem.
"""

def _var_index(i, v, n):
    """Return the SAT variable number for position i and vertex v.
    i and v are 0‑based, n = number of vertices.
    Variables are numbered from 1.
    """
    return i * n + v + 1

def reduce(instance):
    n = instance.get("n")
    edges = instance.get("edges", [])
    # Edge cases: n <= 2 -> always NO, return unsatisfiable formula.
    if n is None or n <= 2:
        # Unsatisfiable: a formula containing an empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for quick lookup.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        if 0 <= u < n and 0 <= v < n:
            adj[u][v] = True
            adj[v][u] = True

    clauses = []
    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)
    # 2. No position i has two vertices (pairwise at most one).
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(i, w, n)])
    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)
    # 4. No vertex appears in two positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])
    # 5. Edge constraints for consecutive positions.
    # For each i (position), consider i_next = (i+1) mod n.
    for i in range(n):
        i_next = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if not adj[u][v]:
                    # forbid u at i and v at i_next
                    clauses.append([-_var_index(i, u, n), -_var_index(i_next, v, n)])
    # Number of variables is n*n.
    return {"num_vars": n * n, "clauses": clauses}

# The module only defines reduce; no top‑level execution.
