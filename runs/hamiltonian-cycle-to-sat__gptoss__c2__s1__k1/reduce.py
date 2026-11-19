import sys

def reduce(instance):
    n = instance["n"]
    edges_input = instance.get("edges", [])
    # Build set of undirected edges (u<v)
    edges = set()
    for u, v in edges_input:
        if u > v:
            u, v = v, u
        edges.add((u, v))

    # Edge cases: n <= 2 -> always NO, produce unsatisfiable formula
    if n <= 2:
        # unsatisfiable SAT instance: one empty clause
        return {"num_vars": 1, "clauses": [[]]}

    # Number of variables: n positions * n vertices
    m = n * n
    clauses = []

    def var(i, v):
        """Return variable number for vertex v at position i (both 0-indexed)."""
        return i * n + v + 1  # variables are 1-indexed

    # 1. Each position i must contain at least one vertex
    for i in range(n):
        clause = [var(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. Each position i contains at most one vertex
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(i, v), -var(i, w)])

    # 3. Each vertex v appears in at least one position
    for v in range(n):
        clause = [var(i, v) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex v appears in at most one position
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, v), -var(j, v)])

    # 5. Consecutive positions must correspond to an edge in the graph
    for i in range(n):
        nxt = (i + 1) % n
        for v in range(n):
            for w in range(n):
                if v == w:
                    continue
                a, b = (v, w) if v < w else (w, v)
                if (a, b) not in edges:
                    clauses.append([-var(i, v), -var(nxt, w)])

    return {"num_vars": m, "clauses": clauses}

# If this file is executed directly, read JSON from stdin and output JSON of reduction.
if __name__ == "__main__":
    import json
    data = json.load(sys.stdin)
    result = reduce(data)
    json.dump(result, sys.stdout)
    sys.stdout.flush()

