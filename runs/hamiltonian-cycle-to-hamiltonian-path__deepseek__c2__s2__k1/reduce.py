def reduce(instance):
    n = instance["n"]
    edges = instance.get("edges", [])

    # Source: n <= 2 is always NO. Target n = 0 is always NO.
    if n <= 2:
        return {"n": 0, "edges": []}

    # Pick vertex 0 as the vertex to split.
    v = 0

    # New vertex labels:
    #   original vertices 1..n-1 become 0..n-2
    #   v1 = n-1, v2 = n, s = n+1, t = n+2
    v1 = n - 1
    v2 = n
    s = n + 1
    t = n + 2

    new_edges = []
    seen = set()

    def add(a, b):
        if a > b:
            a, b = b, a
        if a == b:
            return
        key = (a, b)
        if key not in seen:
            seen.add(key)
            new_edges.append([a, b])

    for e in edges:
        a, b = e[0], e[1]
        if a == v:
            add(v1, b - 1)
            add(v2, b - 1)
        elif b == v:
            add(v1, a - 1)
            add(v2, a - 1)
        else:
            add(a - 1, b - 1)

    # Pendant vertices force the Hamiltonian path to start at s and end at t.
    add(s, v1)
    add(t, v2)

    return {"n": n + 3, "edges": new_edges}
