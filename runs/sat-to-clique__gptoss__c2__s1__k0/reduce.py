import json

def reduce(instance):
    """Reduce SAT instance to Clique instance.
    instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
    Returns: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    clauses = instance.get("clauses", [])
    c = len(clauses)  # number of clauses, target clique size
    # Build list of vertices: each literal in each clause becomes a vertex
    vertices = []  # list of (clause_index, literal)
    for i, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((i, lit))
    n = len(vertices)
    # Map to vertex ids
    # (i, lit) -> id (its index in vertices list)
    # Edges between vertices from different clauses if not contradictory
    edges = []
    for idx1 in range(n):
        i1, lit1 = vertices[idx1]
        var1 = abs(lit1)
        for idx2 in range(idx1 + 1, n):
            i2, lit2 = vertices[idx2]
            if i1 == i2:
                continue  # same clause, no edge
            var2 = abs(lit2)
            # contradictory if same variable with opposite signs
            if var1 == var2 and lit1 != lit2:
                continue
            edges.append([idx1, idx2])
    return {"n": n, "edges": edges, "k": c}

# If this file is run directly, read JSON from stdin and output reduced instance
if __name__ == "__main__":
    import sys
    data = json.load(sys.stdin)
    reduced = reduce(data)
    json.dump(reduced, sys.stdout)
    sys.stdout.flush()
