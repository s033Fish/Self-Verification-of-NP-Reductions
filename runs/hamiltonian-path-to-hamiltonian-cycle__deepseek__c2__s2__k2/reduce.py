"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction
------------
Given a Hamiltonian Path instance G = (V, E) with V = {0, ..., n-1}:

* If n == 1, the source answer is yes, so return a triangle (a yes
  instance of Hamiltonian Cycle).
* Otherwise, add one new vertex x = n and connect it to every original
  vertex.  The resulting graph G' has n + 1 vertices and edges
  E union { [v, n] : v in V }.

Correctness (n != 1)
--------------------
If G has a Hamiltonian path v_1, ..., v_n, then
v_1, ..., v_n, x, v_1 is a Hamiltonian cycle of G'.

Conversely, if G' has a Hamiltonian cycle, the new vertex x has exactly
two neighbours u and v on that cycle (for n >= 2 these are distinct
original vertices).  Removing x from the cycle leaves a Hamiltonian path
from u to v in G.  For n = 0, G' has a single vertex and no cycle, which
matches the source answer no.

The construction runs in O(n + |E|) time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # A single vertex is a Hamiltonian path, but the usual construction
    # would yield a 2-vertex graph, which cannot contain a cycle.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    new_vertex = n
    new_edges = [list(e) for e in edges]
    for v in range(n):
        new_edges.append([v, new_vertex])

    return {"n": n + 1, "edges": new_edges}
