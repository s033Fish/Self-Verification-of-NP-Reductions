"""Reduction from Clique to Vertex Cover.

Given an instance of Clique:
    {"n": n, "edges": [[u, v], ...], "k": k}
we construct the complement graph G' and set k' = n - k.
The resulting instance of VertexCover is:
    {"n": n, "edges": complement_edges, "k": n - k}
This reduction runs in O(n^2) time, polynomial in the input size.
"""

def reduce(instance):
    """Reduce a Clique instance to a VertexCover instance.

    Parameters:
        instance (dict): Clique instance with keys "n", "edges", "k".

    Returns:
        dict: VertexCover instance.
    """
    n = instance.get("n")
    edges = instance.get("edges", [])
    k = instance.get("k")

    # Build a set of existing edges (undirected, ordered as (min, max))
    existing = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Complement edges: all pairs not present in the original graph
    complement = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in existing:
                complement.append([i, j])

    # New k for Vertex Cover
    new_k = n - k

    return {"n": n, "edges": complement, "k": new_k}

# If this file is executed directly, perform a simple self‑test.
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    result = reduce(data)
    json.dump(result, sys.stdout)
    sys.stdout.flush()
