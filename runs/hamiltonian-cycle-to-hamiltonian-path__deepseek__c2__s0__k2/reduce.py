def reduce(instance):
    """
    Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

    Given an undirected graph G = (V, E) with n >= 3, choose a vertex v = 0.
    Construct G' as follows:
      - Keep all vertices of G except v.
      - Add four new vertices v1, v2, p1, p2.
      - Add edges from v1 and v2 to every neighbor of v in G.
      - Add pendant edges p1-v1 and p2-v2.
      - Keep all edges of G not incident to v.
    Then G has a Hamiltonian cycle iff G' has a Hamiltonian path.

    For n <= 2, the source instance is always no, so return the no
    instance of Hamiltonian Path with n = 0.
    """
    n = instance["n"]
    edges = instance["edges"]

    if n <= 2:
        return {"n": 0, "edges": []}

    v = 0

    # Adjacency list of the original graph.
    adj = [set() for _ in range(n)]
    for u, w in edges:
        adj[u].add(w)
        adj[w].add(u)

    # Original vertices except v are relabeled to 0..n-2 (u -> u-1).
    def map_orig(u):
        return u - 1

    # New vertex labels.
    v1 = n - 1
    v2 = n
    p1 = n + 1
    p2 = n + 2
    new_n = n + 3

    new_edges = set()

    # Keep edges of G not incident to v.
    for u, w in edges:
        if u != v and w != v:
            a, b = map_orig(u), map_orig(w)
            if a > b:
                a, b = b, a
            new_edges.add((a, b))

    # Connect v1 and v2 to all neighbors of v.
    for u in adj[v]:
        a = map_orig(u)
        new_edges.add((min(v1, a), max(v1, a)))
        new_edges.add((min(v2, a), max(v2, a)))

    # Pendant edges.
    new_edges.add((min(p1, v1), max(p1, v1)))
    new_edges.add((min(p2, v2), max(p2, v2)))

    return {"n": new_n, "edges": [list(e) for e in new_edges]}
