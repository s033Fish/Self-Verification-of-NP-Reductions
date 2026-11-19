def reduce(instance):
    """
    Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

    Given an undirected graph G = (V, E) with n = |V|, if n <= 2 the source
    is always a no-instance, so we return a trivially no target instance
    (n = 0).  Otherwise pick v = 0, split v into two new vertices
    v_start and v_end, both adjacent to every neighbor of v, and attach a
    new leaf s to v_start and a new leaf t to v_end.  The remaining edges
    are copied.

    Any Hamiltonian path in the constructed graph must have s and t as its
    endpoints (they have degree 1), hence it has the form
        s - v_start - u_1 - ... - u_{n-1} - v_end - t.
    Removing s, v_start, v_end, t gives a Hamiltonian path in G - v whose
    endpoints are neighbours of v, so adding v closes a Hamiltonian cycle
    in G.  Conversely, a Hamiltonian cycle in G through v yields such a
    path.  For n >= 3 the two endpoints of the middle path are distinct,
    so the correspondence is exact.
    """
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: Hamiltonian Cycle is always false.
    if n <= 2:
        return {"n": 0, "edges": []}

    v = 0
    # Relabel the original vertices except v to 0 .. n-2.
    mapping = {i: i - 1 for i in range(1, n)}

    v_start = n - 1
    v_end = n
    s = n + 1
    t = n + 2
    N = n + 3

    new_edges = []
    for u, w in edges:
        if u == v:
            new_edges.append([v_start, mapping[w]])
            new_edges.append([v_end, mapping[w]])
        elif w == v:
            new_edges.append([v_start, mapping[u]])
            new_edges.append([v_end, mapping[u]])
        else:
            new_edges.append([mapping[u], mapping[w]])

    new_edges.append([s, v_start])
    new_edges.append([t, v_end])

    return {"n": N, "edges": new_edges}
