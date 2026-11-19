"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Let G be the source graph on vertices 0..n-1.

For n <= 2 the source is always "no" (a simple graph needs at least three
vertices to contain a cycle), so we return a trivially "no" target instance.

For n >= 3, pick the vertex 0 and build H as follows:

  * remove vertex 0 and add two fresh vertices a and b;
  * for every edge {0, u} of G add the edges {a, u} and {b, u};
  * keep every edge {u, v} of G with u, v != 0;
  * add a fresh pendant leaf la attached only to a;
  * add a fresh pendant leaf lb attached only to b.

Claim: G has a Hamiltonian cycle  <=>  H has a Hamiltonian path.

(=>) If 0, v1, ..., v_{n-1}, 0 is a Hamiltonian cycle of G, then
     lb - b - v1 - ... - v_{n-1} - a - la
     is a Hamiltonian path of H.

(<=) The leaves la and lb have degree 1, so in any Hamiltonian path of H
     they must be the two endpoints.  Hence the path is
     la - a - x1 - x2 - ... - x_{n-1} - b - lb
     where {x1,...,x_{n-1}} are exactly the vertices 1..n-1.  Mapping a and b
     back to 0 turns this into the closed walk
     0 - x1 - x2 - ... - x_{n-1} - 0,
     every consecutive pair of which is an edge of G.  As n >= 3 this is a
     Hamiltonian cycle of G.

The construction uses O(n + m) time and space, so it is polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: the source has no Hamiltonian cycle.  Return a "no" target
    # instance (n = 0 is always "no" for Hamiltonian Path).
    if n <= 2:
        return {"n": 0, "edges": []}

    # New vertex labels.
    a = n          # first copy of vertex 0
    b = n + 1      # second copy of vertex 0
    la = n + 2     # pendant leaf attached to a
    lb = 0         # pendant leaf attached to b (index 0 is free now)

    new_edges = []
    for u, v in edges:
        if u == 0:
            new_edges.append([a, v])
            new_edges.append([b, v])
        elif v == 0:
            new_edges.append([a, u])
            new_edges.append([b, u])
        else:
            new_edges.append([u, v])

    new_edges.append([la, a])
    new_edges.append([lb, b])

    return {"n": n + 3, "edges": new_edges}
