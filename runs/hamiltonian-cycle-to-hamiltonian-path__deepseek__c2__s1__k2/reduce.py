"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Idea
----
A Hamiltonian cycle in G is a Hamiltonian path in G whose two endpoints are
adjacent.  To reduce to the plain Hamiltonian Path problem we pick a vertex
v = 0 and "break" it open:

  * delete v,
  * add two copies v1, v2 of v, each adjacent to every neighbour of v,
  * attach a pendant leaf p1 to v1 and a pendant leaf p2 to v2.

Because p1 and p2 are leaves, every Hamiltonian path of the new graph must
start at p1 and end at p2, so it looks like

        p1 - v1 - x - ... - y - v2 - p2

with x, y neighbours of v.  The middle part x ... y is a Hamiltonian path of
G - v, hence v - x - ... - y - v is a Hamiltonian cycle of G.  Conversely a
Hamiltonian cycle of G through v yields such a path.  This is an exact
equivalence for n >= 3.  Graphs with n <= 2 are always "no" for Hamiltonian
Cycle and are mapped to the empty graph, which is "no" for Hamiltonian Path.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Hamiltonian Cycle is always false for n <= 2.
    if n <= 2:
        return {"n": 0, "edges": []}

    v = 0
    neighbours = set()
    for u, w in edges:
        if u == v:
            neighbours.add(w)
        elif w == v:
            neighbours.add(u)

    # Relabelling:
    #   old vertex u (1 <= u <= n-1)  ->  u - 1        (0 .. n-2)
    #   v1 = n - 1, v2 = n, p1 = n + 1, p2 = n + 2
    v1 = n - 1
    v2 = n
    p1 = n + 1
    p2 = n + 2

    new_edges = []

    # Edges of G that do not touch v.
    for u, w in edges:
        if u == v or w == v:
            continue
        new_edges.append([u - 1, w - 1])

    # v1 and v2 are adjacent to every neighbour of v.
    for a in neighbours:
        new_edges.append([a - 1, v1])
        new_edges.append([a - 1, v2])

    # Pendant leaves force v1 and v2 to be the inner endpoints of the path.
    new_edges.append([v1, p1])
    new_edges.append([v2, p2])

    return {"n": n + 3, "edges": new_edges}
