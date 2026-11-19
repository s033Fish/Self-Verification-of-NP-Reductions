"""Polynomial-time reduction from 3-Coloring to Independent Set.

Given a 3-Coloring instance G = (V, E) with |V| = n, build an
Independent Set instance (G', k) as follows.

* For every vertex v and every colour c in {0, 1, 2}, create a vertex
  (v, c).  Thus G' has 3n vertices.
* For every v, add the three edges among (v, 0), (v, 1), (v, 2), making
  that triple a triangle.  An independent set can therefore use at most
  one colour-copy of each original vertex.
* For every original edge {u, v} and every colour c, add the edge
  between (u, c) and (v, c).  Hence adjacent original vertices cannot
  select the same colour.
* Set k = n.

G has a proper 3-colouring iff G' has an independent set of size n:
from a colouring, take the colour-copy corresponding to each vertex's
colour; conversely, an independent set of size n must contain exactly one
copy of every vertex (each triangle allows at most one), and the
same-colour edges force a proper colouring.

The construction uses O(n + m) vertices and edges, so it runs in
polynomial time.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    target_edges = set()

    # One triangle per original vertex: at most one colour-copy chosen.
    for v in range(n):
        a = 3 * v
        b = 3 * v + 1
        c = 3 * v + 2
        target_edges.add((a, b))
        target_edges.add((a, c))
        target_edges.add((b, c))

    # Same-colour copies of adjacent original vertices cannot both be chosen.
    for u, v in edges:
        for col in range(3):
            a = 3 * u + col
            b = 3 * v + col
            if a > b:
                a, b = b, a
            target_edges.add((a, b))

    return {
        "n": 3 * n,
        "edges": [[u, v] for u, v in sorted(target_edges)],
        "k": n,
    }
