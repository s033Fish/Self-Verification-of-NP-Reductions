import itertools

def reduce(instance):
    n = instance.get("n")
    edges = set()
    for u, v in instance.get("edges", []):
        # store unordered edge as frozenset
        edges.add(frozenset((u, v)))
    # Edge cases
    if n == 0:
        # unsatisfiable: empty clause
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # trivially satisfiable
        return {"num_vars": 0, "clauses": []}
    # variables: x_{i,v} where i position, v vertex
    # variable index = i*n + v + 1 (1-based)
    num_vars = n * n
    clauses = []
    # 1. each position has at least one vertex
    for i in range(n):
        clause = [i * n + v + 1 for v in range(n)]
        clauses.append(clause)
    # 2. each position has at most one vertex
    for i in range(n):
        for u, v in itertools.combinations(range(n), 2):
            clauses.append([-(i * n + u + 1), -(i * n + v + 1)])
    # 3. each vertex appears in at least one position
    for v in range(n):
        clause = [i * n + v + 1 for i in range(n)]
        clauses.append(clause)
    # 4. each vertex appears at most once
    for v in range(n):
        for i, j in itertools.combinations(range(n), 2):
            clauses.append([-(i * n + v + 1), -(j * n + v + 1)])
    # 5. adjacency constraints: forbid non-edges between consecutive positions
    # precompute non-edges ordered pairs
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if frozenset((u, v)) not in edges:
                    # forbid u at i and v at i+1
                    clauses.append([-(i * n + u + 1), -((i + 1) * n + v + 1)])
    return {"num_vars": num_vars, "clauses": clauses}

# The module may be imported; no top-level execution.
