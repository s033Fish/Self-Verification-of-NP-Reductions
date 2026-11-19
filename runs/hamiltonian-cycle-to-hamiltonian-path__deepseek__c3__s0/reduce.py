"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Let G = (V, E) be the source instance with |V| = n.

If n < 3 the source answer is always "no" (a simple graph needs at least
three vertices to contain a cycle), so we return the empty graph
{"n": 0, "edges": []}, which is a "no" instance of Hamiltonian Path.

For n >= 3 pick the vertex v = 0 and build G' as follows:

  * Delete v and replace it by two "twin" vertices v1, v2 that inherit
    exactly the neighbourhood of v (each neighbour u of v becomes adjacent
    to both v1 and v2).
  * Add two pendant vertices p1 (attached only to v1) and p2 (attached
    only to v2).

Claim: G has a Hamiltonian cycle  <=>  G' has a Hamiltonian path.

(=>) A Hamiltonian cycle of G visits v; let a and b be the two neighbours
     of v on the cycle.  Removing v leaves a Hamiltonian path a ... b of
     G - v.  Then p1 - v1 - a - ... - b - v2 - p2 is a Hamiltonian path
     of G'.

(<=) p1 and p2 have degree 1, so in any Hamiltonian path of G' they are
     the two endpoints (if v were isolated, G' would be disconnected and
     no Hamiltonian path would exist at all).  The path therefore reads
     p1 - v1 - a - ... - b - v2 - p2, where a and b are neighbours of v in
     G and a ... b is a Hamiltonian path of G - v.  Adding v closes it
     into the Hamiltonian cycle v - a - ... - b - v of G.

The construction uses O(n + m) time and space.
"""


def reduce(instance):
    """Reduce a Hamiltonian Cycle instance to a Hamiltonian Path instance."""
    n = instance["n"]
    edges = instance["edges"]

    if n < 3:
        return {"n": 0, "edges": []}

    # Original vertices 1..n-1 are kept, remapped to 0..n-2.
    # v1 = n-1, v2 = n, p1 = n+1, p2 = n+2.
    v1 = n - 1
    v2 = n
    p1 = n + 1
    p2 = n + 2
    new_n = n + 3

    new_edges = []
    for u, w in edges:
        if u == 0:
            new_edges.append([v1, w - 1])
            new_edges.append([v2, w - 1])
        elif w == 0:
            new_edges.append([v1, u - 1])
            new_edges.append([v2, u - 1])
        else:
            new_edges.append([u - 1, w - 1])

    new_edges.append([p1, v1])
    new_edges.append([p2, v2])

    return {"n": new_n, "edges": new_edges}
