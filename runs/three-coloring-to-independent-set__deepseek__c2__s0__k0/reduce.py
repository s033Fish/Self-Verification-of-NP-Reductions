"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction
------------
Given a 3-Coloring instance G = (V, E) with |V| = n, build an Independent
Set instance H as follows.

* For every original vertex v and every colour c in {0, 1, 2}, create a
  target vertex (v, c).  The target graph therefore has 3n vertices.
* For every original vertex v, add the triangle
  (v, 0) -- (v, 1) -- (v, 2) -- (v, 0).
  An independent set may contain at most one of these three vertices, so
  it can choose at most one colour for v.
* For every original edge {u, v} and every colour c, add the edge
  (u, c) -- (v, c).
  This forbids assigning the same colour c to both endpoints of an
  original edge.

Set k = n.

Correctness
-----------
If G has a proper 3-colouring, selecting (v, colour(v)) for every vertex v
gives n vertices.  Two selected vertices with different original vertices
cannot be adjacent because the only edges between colour classes of
different original vertices are (u, c) -- (v, c), and adjacent original
vertices receive different colours.  Two selected vertices with the same
original vertex do not exist because exactly one colour per vertex is
selected.  Hence H has an independent set of size n.

Conversely, an independent set of size n in H must contain exactly one
vertex from each of the n triangles, so it defines one colour per original
vertex.  If two adjacent original vertices u and v received the same colour
c, the selected vertices (u, c) and (v, c) would be adjacent, a
contradiction.  Thus the colouring is proper.

Therefore H is a yes-instance of Independent Set (independent set of size
at least k = n) exactly when G is 3-colourable.

The construction uses O(n + |E|) vertices and edges and runs in
polynomial time.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    new_edges = []
    seen = set()

    def add_edge(a, b):
        key = (a, b) if a < b else (b, a)
        if key not in seen:
            seen.add(key)
            new_edges.append([key[0], key[1]])

    def vertex(v, colour):
        return 3 * v + colour

    # One triangle per original vertex: at most one colour may be chosen.
    for v in range(n):
        add_edge(vertex(v, 0), vertex(v, 1))
        add_edge(vertex(v, 1), vertex(v, 2))
        add_edge(vertex(v, 0), vertex(v, 2))

    # For each original edge, forbid equal colours at its endpoints.
    for u, v in edges:
        for colour in range(3):
            add_edge(vertex(u, colour), vertex(v, colour))

    return {"n": 3 * n, "edges": new_edges, "k": n}
