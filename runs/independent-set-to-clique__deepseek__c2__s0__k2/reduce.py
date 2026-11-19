def reduce(instance):
    """Reduce Independent Set to Clique by taking the complement graph.

    An independent set of size at least k in G is exactly a clique of size
    at least k in the complement of G, so we keep n and k unchanged and
    replace the edge set with all missing undirected pairs.
    """
    n = instance["n"]
    k = instance["k"]

    existing = set()
    for u, v in instance.get("edges", []):
        if u > v:
            u, v = v, u
        existing.add((u, v))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
