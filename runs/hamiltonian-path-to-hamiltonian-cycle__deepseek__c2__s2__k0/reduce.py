"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction
------------
Given a Hamiltonian Path instance G = (V, E) with V = {0, ..., n-1}:

* If n == 1, the source is always yes.  The standard construction would
  produce a 2-vertex graph, and no simple graph on <= 2 vertices has a
  cycle, so we instead return a triangle (3 vertices, 3 edges), which is
  always yes.

* Otherwise add one new vertex `n` and connect it to every original
  vertex.  Return G' = ({0, ..., n}, E union {{n, v} : v in V}).

Correctness (n >= 2)
--------------------
If G has a Hamiltonian path v_0, ..., v_{n-1}, then
v_0, ..., v_{n-1}, n, v_0 is a Hamiltonian cycle of G' (the two closing
edges exist because n is universal).

Conversely, if G' has a Hamiltonian cycle, the universal vertex n has
exactly two neighbours a, b on that cycle.  Removing n from the cycle
leaves a Hamiltonian path of G from a to b (a != b because n >= 2, so
the cycle has at least 3 vertices).

The construction uses O(n + m) time and adds exactly n edges, so it is
polynomial.  For n = 0 the result is a single isolated vertex (no cycle),
matching the source answer "no".
"""


def reduce(instance):
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n == 1 is the only degenerate case where the standard reduction
    # fails: the source is yes, but the constructed graph would have only
    # two vertices and hence no cycle.  A triangle is always yes.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    new_vertex = n
    new_edges = [list(edge) for edge in edges]
    for v in range(n):
        new_edges.append([new_vertex, v])

    return {"n": n + 1, "edges": new_edges}
