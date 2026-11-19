import itertools

def reduce(instance):
    """Reduce Clique instance to Vertex Cover instance.
    Input instance format:
        {"n": n, "edges": [[u, v], ...], "k": k}
    Output instance format (Vertex Cover): same keys.
    """
    n = instance["n"]
    k = instance["k"]
    # Build set of existing edges (unordered)
    edge_set = set()
    for u, v in instance.get("edges", []):
        if u > v:
            u, v = v, u
        edge_set.add((u, v))
    # Complement edges: all unordered pairs not in edge_set, u!=v
    comp_edges = []
    for u, v in itertools.combinations(range(n), 2):
        if (u, v) not in edge_set:
            comp_edges.append([u, v])
    # Target k = n - k_original
    k_target = n - k
    return {"n": n, "edges": comp_edges, "k": k_target}

