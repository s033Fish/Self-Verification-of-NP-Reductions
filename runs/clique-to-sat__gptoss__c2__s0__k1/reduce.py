"""Reduction from Clique to SAT.

Source problem (Clique) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
Target problem (Sat) instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}

The reduction runs in polynomial time and produces a SAT formula that is
satisfiable iff the input graph has a clique of size at least k.
"""

def reduce(instance):
    n = instance.get("n")
    edges = instance.get("edges", [])
    k = instance.get("k")

    # Edge cases handling
    if k <= 0:
        # Always yes: return trivially satisfiable formula (no clauses)
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        # Yes iff n >= 1
        if n >= 1:
            return {"num_vars": 0, "clauses": []}
        else:
            return {"num_vars": 0, "clauses": [[]]}  # unsat
    if k > n:
        # Always no: return unsatisfiable formula (single empty clause)
        return {"num_vars": 0, "clauses": [[]]}
    # General case: k >= 2 and k <= n
    # Build adjacency set for quick edge lookup
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    # Variable mapping: (position i, vertex v) -> var index (1-based)
    # i ranges 0..k-1, v ranges 0..n-1
    def var(i, v):
        return i * n + v + 1  # +1 for 1-based indexing

    num_vars = k * n
    clauses = []

    # 1. Each position i must be occupied by at least one vertex
    for i in range(k):
        clause = [var(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. No vertex appears in two different positions
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var(i, v), -var(j, v)])

    # 3. Non-edges cannot both be selected
    # Precompute list of unordered non-edges (u, v) with u < v and not an edge
    non_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if not adj[u][v]:
                non_edges.append((u, v))

    for i in range(k):
        for j in range(i + 1, k):
            for (u, v) in non_edges:
                # forbid selecting u at position i and v at position j
                clauses.append([-var(i, u), -var(j, v)])
                # forbid selecting v at position i and u at position j
                clauses.append([-var(i, v), -var(j, u)])

    return {"num_vars": num_vars, "clauses": clauses}

# The module may be imported; expose the function name expected by the grader.
__all__ = ["reduce"]

