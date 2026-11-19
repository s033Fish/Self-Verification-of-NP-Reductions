def reduce(instance):
    """Polynomial reduction from Vertex Cover to Dominating Set.

    Given G = (V, E) and integer k, build G' as follows:
      * keep all original vertices and all original edges;
      * for every edge e = (u, v), add a new vertex x_e adjacent to u and v.

    Let i be the number of isolated vertices of G.  The target budget is
    k' = k + i.

    Equivalence:
      * If C is a vertex cover of G with |C| <= k, then C plus all isolated
        vertices dominates G' (each edge-vertex x_e is adjacent to an endpoint
        in C, and every non-isolated vertex is either in C or adjacent to an
        endpoint in C).
      * If D is a dominating set of G' with |D| <= k + i, then every x_e in D
        can be replaced by one of its endpoints without increasing the size
        (the endpoint also dominates the other endpoint through the original
        edge).  Thus there is a dominating set D' subset of V(G) with
        |D'| <= k + i.  All isolated vertices must be in D', so removing them
        leaves a vertex cover of G of size at most k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1

    isolated = sum(1 for d in degree if d == 0)

    new_edges = []
    for u, v in edges:
        new_edges.append([u, v])

    for i, (u, v) in enumerate(edges):
        x = n + i
        new_edges.append([u, x])
        new_edges.append([v, x])

    return {
        "n": n + len(edges),
        "edges": new_edges,
        "k": k + isolated,
    }
