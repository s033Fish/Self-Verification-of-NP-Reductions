def reduce(instance):
    """Reduce Vertex Cover instance to Set Cover instance.

    VertexCover instance format:
        {"n": int, "edges": [[u, v], ...], "k": int}
    SetCover instance format:
        {"universe_size": int, "sets": [[element, ...], ...], "k": int}
    """
    n = instance.get("n", 0)
    edges = instance.get("edges", [])
    k = instance.get("k", 0)

    # Universe elements correspond to edges, indexed 0..|E|-1
    universe_size = len(edges)
    # For each vertex, collect indices of incident edges
    sets = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        # Assuming vertices are valid indices
        sets[u].append(idx)
        sets[v].append(idx)
    return {"universe_size": universe_size, "sets": sets, "k": k}

