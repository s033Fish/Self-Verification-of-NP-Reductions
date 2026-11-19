"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction
------------
Given a 3-Coloring instance G = (V, E) with n = |V|, build an Independent
Set instance H as follows.

* For every vertex v in V and every colour c in {0, 1, 2}, create one
  vertex (v, c) of H.  Thus H has 3n vertices.
* For every v, add the three edges joining the pairs of colour copies of
  v, i.e. (v,0)-(v,1), (v,0)-(v,2), (v,1)-(v,2).  An independent set can
  therefore use at most one colour copy of each original vertex.
* For every original edge {u, v} and every colour c, add the edge
  (u,c)-(v,c).  This forbids u and v from receiving the same colour.
* Set k = n.

Correctness
-----------
If G has a proper 3-colouring, picking (v, colour(v)) for every v gives
n pairwise non-adjacent vertices of H, so H has an independent set of
size n.

Conversely, any independent set of H contains at most one copy of each
original vertex, hence has size at most n.  If it has size exactly n it
contains exactly one copy of each vertex; the cross edges guarantee that
the chosen colours form a proper 3-colouring of G.

Therefore H has an independent set of size at least n iff G is
3-colourable.  The construction uses O(n + |E|) vertices/edges and runs
in polynomial time.
"""


def reduce(instance):
    """Map a 3-Coloring instance to an equivalent Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    # One target vertex for each (original vertex, colour) pair.
    num_colors = 3
    target_n = n * num_colors

    def node(v, c):
        return v * num_colors + c

    target_edges = []

    # A vertex may take at most one colour.
    for v in range(n):
        target_edges.append([node(v, 0), node(v, 1)])
        target_edges.append([node(v, 0), node(v, 2)])
        target_edges.append([node(v, 1), node(v, 2)])

    # Adjacent original vertices may not share a colour.
    for u, v in edges:
        for c in range(num_colors):
            target_edges.append([node(u, c), node(v, c)])

    return {"n": target_n, "edges": target_edges, "k": n}
