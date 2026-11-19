"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction
------------
Given a 3-Coloring instance G = (V, E) with V = {0, ..., n-1}, build an
Independent Set instance (G', k) as follows.

* For every vertex v and every colour c in {0, 1, 2}, create a vertex
  (v, c) of G'.  Encode it as the integer 3*v + c, so G' has 3n vertices.
* For every vertex v, add the triangle
      (v,0)-(v,1), (v,1)-(v,2), (v,0)-(v,2).
  An independent set can therefore contain at most one colour-vertex per
  original vertex.
* For every edge {u, w} of G and every colour c, add the edge
      (u,c)-(w,c).
  This forbids the two endpoints of an edge from receiving the same colour.
* Set k = n.

Correctness
-----------
(=>) A proper 3-colouring of G picks, for each vertex v, the colour-vertex
(v, colour(v)).  These n vertices are pairwise non-adjacent: two chosen
vertices from the same original vertex are impossible (one per vertex),
and an edge between (u,c) and (w,c) would mean colour(u) = colour(w) = c
for an edge {u,w}, contradicting properness.  So G' has an independent set
of size n.

(<=) An independent set of size n in G' contains at most one vertex from
each of the n triangles, hence exactly one (v, colour(v)) per original
vertex.  If {u,w} were an edge of G with colour(u) = colour(w) = c, then
(u,c) and (w,c) would both be in the set and adjacent, a contradiction.
Thus the assignment is a proper 3-colouring of G.

The construction uses O(n + |E|) vertices/edges and runs in polynomial
time; no brute-force solver is invoked.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    new_edges = []

    # One triangle per original vertex: at most one colour may be chosen.
    for v in range(n):
        base = 3 * v
        new_edges.append([base + 0, base + 1])
        new_edges.append([base + 1, base + 2])
        new_edges.append([base + 0, base + 2])

    # For each original edge, forbid equal colours at its two endpoints.
    for u, w in edges:
        for c in range(3):
            new_edges.append([3 * u + c, 3 * w + c])

    return {"n": 3 * n, "edges": new_edges, "k": n}
