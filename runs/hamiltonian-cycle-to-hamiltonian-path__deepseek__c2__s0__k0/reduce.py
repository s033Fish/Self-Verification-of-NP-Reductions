"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Given an undirected graph G on vertices 0..n-1 with n >= 3, pick the vertex
v = n-1 and build a graph G' as follows:

  * delete v;
  * add two copies v1, v2 of v, each joined to every neighbour of v;
  * add a fresh pendant leaf p1 attached to v1 and a fresh pendant leaf p2
    attached to v2.

So G' has n + 3 vertices: the original vertices 0..n-2, plus v1, v2, p1, p2.

Correctness
-----------
(=>) If G has a Hamiltonian cycle, it visits v between two neighbours a and b.
Removing v leaves a Hamiltonian path a..b of G - v.  Then
p1 - v1 - a - ... - b - v2 - p2 is a Hamiltonian path of G'.

(<=) In any Hamiltonian path of G', the leaves p1 and p2 (degree 1) must be
the two endpoints, so the path is p1 - v1 - ... - v2 - p2.  The neighbours of
v1 and v2 along this path are neighbours of v (the only other neighbours they
have are the leaves), hence deleting v1 and v2 leaves a Hamiltonian path a..b
of G - v with a, b adjacent to v.  Adding v closes it into a Hamiltonian
cycle v - a - ... - b - v of G.

For n < 3 the source is always "no"; {"n": 0, "edges": []} is a valid "no"
instance of Hamiltonian Path, so it is returned in that case.

The construction uses O(|E|) time and space.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Hamiltonian Cycle is always no for n <= 2 (including n = 0).
    # n = 0 is a valid always-no instance of Hamiltonian Path.
    if n < 3:
        return {"n": 0, "edges": []}

    v = n - 1          # vertex to split
    v1 = n - 1         # first copy of v (label freed by deleting v)
    v2 = n             # second copy of v
    p1 = n + 1         # pendant attached to v1
    p2 = n + 2         # pendant attached to v2

    new_edges = []
    neighbours = []
    for u, w in edges:
        if u == v:
            neighbours.append(w)
        elif w == v:
            neighbours.append(u)
        else:
            new_edges.append([u, w])

    for x in neighbours:
        new_edges.append([v1, x])
        new_edges.append([v2, x])

    new_edges.append([p1, v1])
    new_edges.append([p2, v2])

    return {"n": n + 3, "edges": new_edges}
