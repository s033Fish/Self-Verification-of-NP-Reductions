def reduce(instance):
    """
    Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

    Given a source graph G, choose a vertex v.  Build G' by adding:
      x -- v
      y -- u   for every neighbor u of v
      y -- z
    where x, y, z are new vertices.

    G has a Hamiltonian cycle iff G' has a Hamiltonian path.
    """
    n = instance["n"]
    edges = instance.get("edges", [])

    # Hamiltonian Cycle is always false for n <= 2.
    if n <= 2:
        return {"n": 0, "edges": []}

    # Adjacency of the source graph.
    adj = [set() for _ in range(n)]
    for u, w in edges:
        adj[u].add(w)
        adj[w].add(u)

    # Choose any vertex; 0 is always valid because n >= 3.
    v = 0
    neighbors = sorted(adj[v])

    # New vertex labels.
    x = n          # leaf attached to v
    y = n + 1      # connector to all neighbors of v
    z = n + 2      # leaf attached to y

    new_edges = []
    seen = set()

    def add_edge(a, b):
        if a > b:
            a, b = b, a
        if (a, b) not in seen:
            seen.add((a, b))
            new_edges.append([a, b])

    # Keep all original edges (canonicalized and deduplicated).
    for u, w in edges:
        add_edge(u, w)

    # Attach the gadget.
    add_edge(v, x)
    for u in neighbors:
        add_edge(u, y)
    add_edge(y, z)

    return {"n": n + 3, "edges": new_edges}
