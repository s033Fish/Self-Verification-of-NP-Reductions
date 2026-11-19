"""Reduction from Clique to Vertex Cover.

Given an instance of Clique:
    {"n": n, "edges": [[u, v], ...], "k": k}
we construct an instance of VertexCover on the complement graph with
parameter k' = n - k.

The reduction runs in polynomial time (O(n^2)) and satisfies:
    Clique instance is YES iff the resulting VertexCover instance is YES.
"""

def reduce(instance):
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n", "edges", and "k" describing a graph
        for the Clique problem.

    Returns
    -------
    dict
        A dictionary representing an instance of the VertexCover problem.
    """
    n = instance["n"]
    edges = instance.get("edges", [])
    k = instance["k"]

    # Build a set of existing edges for O(1) lookup. Use frozenset for unordered pair.
    edge_set = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Complement edges: all unordered pairs not present in the original graph.
    comp_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                comp_edges.append([u, v])

    # New k for VertexCover is n - k.
    new_k = n - k
    return {"n": n, "edges": comp_edges, "k": new_k}

# If this file is run directly, perform a simple sanity check.
if __name__ == "__main__":
    import json, sys
    if len(sys.argv) != 2:
        print("Usage: python reduce.py <instance.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        inst = json.load(f)
    out = reduce(inst)
    print(json.dumps(out, indent=2))

