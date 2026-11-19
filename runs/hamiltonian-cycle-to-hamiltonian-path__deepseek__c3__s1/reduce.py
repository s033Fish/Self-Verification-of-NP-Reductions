"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Given an undirected graph G on n >= 3 vertices, pick a vertex v (we use 0)
and split it into two new vertices v1, v2, each adjacent to exactly the
neighbours of v (v1 and v2 are not adjacent to each other).  Call this G'.

Claim: G has a Hamiltonian cycle iff G' has a Hamiltonian path whose
endpoints are v1 and v2.

  * (=>) Break the cycle v, a, ..., b, v at v.  Then v1, a, ..., b, v2 is a
    Hamiltonian path of G' from v1 to v2.
  * (<=) A Hamiltonian path v1, p1, ..., p_{n-1}, v2 of G' has p1 and
    p_{n-1} in N(v) (the only neighbours of v1/v2).  Since n >= 3 we have
    p1 != p_{n-1}, so v, p1, ..., p_{n-1}, v is a Hamiltonian cycle of G.

To turn the "specified endpoints" version into ordinary Hamiltonian Path we
add two leaves u (adjacent to v1) and w (adjacent to v2).  Leaves must be
endpoints of any Hamiltonian path, so G' has a v1-v2 Hamiltonian path iff
G'' = G' + {u,w} has a Hamiltonian path (necessarily u ... w).

For n <= 2 the source is always no, so we return the always-no instance
{"n": 0, "edges": []}.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Hamiltonian Cycle is always no for n <= 2.
    if n <= 2:
        return {"n": 0, "edges": []}

    v = 0  # vertex to split

    # Relabel the surviving original vertices 1..n-1 -> 0..n-2.
    def m(i):
        return i - 1

    v1 = n - 1   # first copy of v
    v2 = n       # second copy of v
    u = n + 1    # leaf attached to v1
    w = n + 2    # leaf attached to v2

    new_edges = []
    seen = set()

    def add(a, b):
        if a == b:
            return
        key = (a, b) if a < b else (b, a)
        if key in seen:
            return
        seen.add(key)
        new_edges.append([a, b])

    for a, b in edges:
        if a == v or b == v:
            x = b if a == v else a
            add(v1, m(x))
            add(v2, m(x))
        else:
            add(m(a), m(b))

    add(u, v1)
    add(w, v2)

    return {"n": n + 3, "edges": new_edges}
