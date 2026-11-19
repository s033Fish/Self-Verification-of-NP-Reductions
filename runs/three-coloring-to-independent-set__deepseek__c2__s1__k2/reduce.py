"""Polynomial-time reduction from 3-Coloring to Independent Set.

Source instance:  {"n": n, "edges": [[u, v], ...]}
Target instance:  {"n": N, "edges": [[u, v], ...], "k": k}

Construction (standard "gadget" reduction):
  * For every vertex v of the source graph create three vertices
    3*v, 3*v+1, 3*v+2, one for each of the three colours.
  * Join the three copies of each vertex with a triangle so that at most
    one colour can be chosen for that vertex.
  * For every source edge {u, v} and every colour c, add the edge
    {3*u + c, 3*v + c}, forbidding the same colour on both endpoints.
  * Set k = n (the number of source vertices).

The source graph is 3-colourable iff the constructed graph has an
independent set of size at least n: a proper 3-colouring picks exactly one
copy of each vertex (an independent set of size n), and conversely any
independent set of size n must pick exactly one copy per vertex triangle
and those choices form a proper colouring.

Runs in O(n + m) time, hence polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    new_edges = []

    # Triangle for every original vertex: at most one colour per vertex.
    for v in range(n):
        a, b, c = 3 * v, 3 * v + 1, 3 * v + 2
        new_edges.append([a, b])
        new_edges.append([b, c])
        new_edges.append([a, c])

    # Same-colour conflict edges for every original edge.
    seen = set()
    for e in edges:
        u, v = e[0], e[1]
        if u == v:
            continue
        key = (u, v) if u < v else (v, u)
        if key in seen:
            continue
        seen.add(key)
        for col in range(3):
            new_edges.append([3 * u + col, 3 * v + col])

    return {"n": 3 * n, "edges": new_edges, "k": n}
