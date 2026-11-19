"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction
------------
Given a Hamiltonian Path instance G = (V, E) with V = {0, ..., n-1}:

* If n == 0, the source answer is "no".  Return the empty graph
  {"n": 0, "edges": []}, which is also "no" for Hamiltonian Cycle.

* If n == 1, the source answer is "yes" (a single vertex is a path), but
  the standard gadget would yield a 2-vertex graph, which can never have a
  cycle.  Return the triangle on 3 vertices, which is "yes".

* If n >= 2, add one new vertex x = n and connect it to every original
  vertex.  The resulting graph G' has vertex set {0, ..., n} and edge set
  E union {[x, v] : v in V}.

Correctness for n >= 2
----------------------
(=>) If v1, ..., vn is a Hamiltonian path of G, then
     x, v1, ..., vn, x is a Hamiltonian cycle of G'.

(<=) If G' has a Hamiltonian cycle, the new vertex x has degree exactly n
     and its only neighbours are original vertices.  In the cycle x has two
     distinct neighbours a and b, so deleting x (and its two cycle edges)
     leaves a path from a to b through all n original vertices, i.e. a
     Hamiltonian path of G.

The construction adds one vertex and n edges, so it runs in O(n + |E|)
time and is clearly polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # No Hamiltonian path exists on an empty graph; the empty graph also has
    # no Hamiltonian cycle.
    if n == 0:
        return {"n": 0, "edges": []}

    # A single vertex is a Hamiltonian path, but no graph on <= 2 vertices
    # has a Hamiltonian cycle.  Emit a triangle, which is a "yes" instance.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # Standard gadget: add a universal new vertex x = n.
    x = n
    new_edges = [list(edge) for edge in edges]
    for v in range(n):
        new_edges.append([x, v])

    return {"n": n + 1, "edges": new_edges}
