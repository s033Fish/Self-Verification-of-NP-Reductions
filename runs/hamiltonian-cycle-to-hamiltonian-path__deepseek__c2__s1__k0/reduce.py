"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Idea
----
Given an undirected graph G on vertices 0..n-1, pick the vertex v = 0 and
"split" it into two copies v_in and v_out.  Add a pendant vertex p attached
only to v_in and a pendant vertex q attached only to v_out.  Every edge
{v, u} of G becomes the two edges {v_in, u} and {v_out, u}; all other edges
of G are kept.

Claim: G has a Hamiltonian cycle iff the constructed graph G' has a
Hamiltonian path.

(=>) If v, a1, a2, ..., a_{n-1}, v is a Hamiltonian cycle of G, then
     p - v_in - a1 - a2 - ... - a_{n-1} - v_out - q is a Hamiltonian path
     of G'.

(<=) In G', p and q have degree 1, so in any Hamiltonian path they must be
     the two endpoints.  The path therefore has the form
     p - v_in - a1 - ... - a_{n-1} - v_out - q, where a1..a_{n-1} is a
     permutation of the other vertices of G.  Since v_in is adjacent to a1
     and v_out is adjacent to a_{n-1}, the sequence
     v - a1 - ... - a_{n-1} - v is a Hamiltonian cycle of G.

Edge cases: for n < 3 the source is always "no" (a simple graph needs at
least three vertices for a cycle), so we return the target no-instance
{"n": 0, "edges": []}.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Hamiltonian Cycle is always false for n <= 2 (including n = 0).
    if n < 3:
        return {"n": 0, "edges": []}

    # Relabel the original vertices other than 0 as 0..n-2.
    # New vertices: v_in = n-1, v_out = n, p = n+1, q = n+2.
    v_in = n - 1
    v_out = n
    p = n + 1
    q = n + 2

    new_edges = []
    seen = set()

    def add(a, b):
        if a > b:
            a, b = b, a
        key = (a, b)
        if key not in seen:
            seen.add(key)
            new_edges.append([a, b])

    for u, w in edges:
        if u == 0:
            add(v_in, w - 1)
            add(v_out, w - 1)
        elif w == 0:
            add(v_in, u - 1)
            add(v_out, u - 1)
        else:
            add(u - 1, w - 1)

    # Pendant vertices force v_in and v_out to be the path endpoints.
    add(p, v_in)
    add(q, v_out)

    return {"n": n + 3, "edges": new_edges}
