import itertools

def reduce(instance):
    """Reduce Hamiltonian Path instance to SAT instance.
    instance: dict with keys 'n' and 'edges' as described.
    Returns: dict with keys 'num_vars' and 'clauses'.
    """
    n = instance.get('n')
    edges = instance.get('edges', [])
    # Edge set for quick lookup (undirected)
    edge_set = set()
    for u, v in edges:
        if u == v:
            continue
        a, b = min(u, v), max(u, v)
        edge_set.add((a, b))
    # Helper to map (position, vertex) to variable number (1-indexed)
    def var(i, v):
        # i and v are 0-based
        return i * n + v + 1
    clauses = []
    # Edge cases: n == 0 -> unsatisfiable (empty clause)
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}
    # 1. Each position i has at least one vertex
    for i in range(n):
        clause = [var(i, v) for v in range(n)]
        clauses.append(clause)
    # 2. Each position i has at most one vertex
    for i in range(n):
        for v1, v2 in itertools.combinations(range(n), 2):
            clauses.append([-var(i, v1), -var(i, v2)])
    # 3. Each vertex appears in at least one position
    for v in range(n):
        clause = [var(i, v) for i in range(n)]
        clauses.append(clause)
    # 4. Each vertex appears at most once
    for v in range(n):
        for i1, i2 in itertools.combinations(range(n), 2):
            clauses.append([-var(i1, v), -var(i2, v)])
    # 5. Edge consistency for consecutive positions
    # Precompute non-edges (including self-loops which are not allowed)
    all_pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    non_edges = []
    for u, v in all_pairs:
        a, b = min(u, v), max(u, v)
        if (a, b) not in edge_set:
            non_edges.append((u, v))
    for i in range(n - 1):
        for u, v in non_edges:
            # forbid u at position i and v at i+1
            clauses.append([-var(i, u), -var(i + 1, v)])
    # Number of variables
    num_vars = n * n
    return {"num_vars": num_vars, "clauses": clauses}

# If run as script, allow simple testing
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    result = reduce(data)
    json.dump(result, sys.stdout)
    sys.stdout.flush()

