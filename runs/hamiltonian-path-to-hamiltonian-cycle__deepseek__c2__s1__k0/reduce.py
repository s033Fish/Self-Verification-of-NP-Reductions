"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

SOURCE: HamiltonianPath  (undirected, any endpoints)
TARGET: HamiltonianCycle (undirected)

Construction
------------
Given an instance G = (V, E) of Hamiltonian Path with V = {0, ..., n-1},
build G' by adding one new vertex w = n and connecting it to every vertex
of G:

    G' = ({0, ..., n}, E union { [v, n] : v in V }).

Claim (for n >= 2): G has a Hamiltonian path iff G' has a Hamiltonian cycle.

  (=>) If v_1, v_2, ..., v_n is a Hamiltonian path in G, then
       w, v_1, v_2, ..., v_n, w is a Hamiltonian cycle in G'.

  (<=) If G' has a Hamiltonian cycle, deleting w from it leaves a path
       through all n original vertices that uses only edges of G (the two
       cycle-neighbours of w become the path endpoints).  Hence G has a
       Hamiltonian path.

Edge cases
----------
* n = 0: the source answer is "no".  The construction yields one isolated
  vertex (n' = 1), which has no cycle, so the target answer is also "no".
* n = 1: the source answer is "yes", but the construction would yield only
  two vertices, which can never contain a cycle.  We therefore emit a
  triangle, which is a "yes" instance of Hamiltonian Cycle.
* n = 2: with the edge [0, 1] the construction is the triangle (yes); with
  no edge it is a path 0-w-1 (no cycle), matching the source exactly.

The construction adds n edges and one vertex, so it runs in O(n + m) time.
"""


def reduce(instance):
    """Map a Hamiltonian Path instance to a Hamiltonian Cycle instance.

    The returned instance is "yes" for Hamiltonian Cycle exactly when the
    input is "yes" for Hamiltonian Path.
    """
    n = instance["n"]
    edges = instance["edges"]

    # n == 1 is the only case the one-universal-vertex gadget cannot handle:
    # the gadget has 2 vertices and can never contain a cycle.  Emit a
    # triangle instead (a valid "yes" Hamiltonian Cycle instance).
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    w = n  # the new universal vertex

    new_edges = [[u, v] for u, v in edges]
    for v in range(n):
        new_edges.append([v, w])

    return {"n": n + 1, "edges": new_edges}
