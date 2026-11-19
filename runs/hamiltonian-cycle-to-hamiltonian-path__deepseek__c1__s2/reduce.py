"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Given an undirected graph G = (V, E) on n vertices, we build a graph H
such that G has a Hamiltonian cycle iff H has a Hamiltonian path.

Construction (for n >= 3):
    Pick the vertex v = 0 and split it into two copies v1 and v2.
    Every neighbour u of v becomes adjacent to both v1 and v2.
    Add two fresh pendant vertices s and t with the single edges s-v1
    and t-v2.  All other vertices/edges of G are kept unchanged.

Correctness:
    (=>) If v, u1, ..., u_{n-1}, v is a Hamiltonian cycle of G, then
         s, v1, u1, ..., u_{n-1}, v2, t is a Hamiltonian path of H.
    (<=) In any Hamiltonian path of H, the degree-1 vertices s and t
         must be the two endpoints, so the path is
         s, v1, u1, ..., u_{n-1}, v2, t.  Since u1 is adjacent to v1
         and u_{n-1} to v2, v, u1, ..., u_{n-1}, v is a Hamiltonian
         cycle of G.

Edge cases:
    n <= 2 is always "no" for Hamiltonian Cycle.  The gadget would be
    wrong for n = 2 (an edge 0-1 yields the path s-v1-1-v2-t), so those
    instances are mapped to the always-"no" empty graph.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Hamiltonian Cycle is always no for n <= 2.
    if n <= 2:
        return {"n": 0, "edges": []}

    # Split vertex 0 into v1 = n-1 and v2 = n; pendants s = n+1, t = n+2.
    # Original vertices 1..n-1 are relabelled to 0..n-2.
    v1 = n - 1
    v2 = n
    s = n + 1
    t = n + 2

    new_edges = []
    neighbours_of_v = set()

    for u, w in edges:
        if u == 0:
            neighbours_of_v.add(w)
        elif w == 0:
            neighbours_of_v.add(u)
        else:
            new_edges.append([u - 1, w - 1])

    for u in neighbours_of_v:
        new_edges.append([u - 1, v1])
        new_edges.append([u - 1, v2])

    new_edges.append([s, v1])
    new_edges.append([t, v2])

    return {"n": n + 3, "edges": new_edges}
