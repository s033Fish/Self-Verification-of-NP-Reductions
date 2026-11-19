"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction
------------
Given a Hamiltonian Path instance G = (V, E) with V = {0, ..., n-1}:

* n == 0: G has no Hamiltonian path.  Return the empty graph, which has no
  Hamiltonian cycle.

* n == 1: G trivially has a Hamiltonian path (the single vertex).  The
  standard construction (add one universal vertex) would yield a graph on
  2 vertices, which can never have a cycle.  Instead return the triangle on
  {0, 1, 2}, which does have a Hamiltonian cycle.

* n >= 2: add one new vertex x = n and connect it to every original vertex.
  Call the result G'.  Then G has a Hamiltonian path iff G' has a
  Hamiltonian cycle:
    - If v_1, ..., v_n is a Hamiltonian path of G, then
      x, v_1, ..., v_n, x is a Hamiltonian cycle of G'.
    - If G' has a Hamiltonian cycle, it visits x and uses exactly two edges
      incident to x, say {x, a} and {x, b}.  Removing x from the cycle
      leaves a Hamiltonian path a, ..., b of G.

The construction adds one vertex and n edges, so it runs in polynomial time
(linear in the size of the instance).  No brute-force solver is used.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    if n == 0:
        # Source is no; empty target graph is also no.
        return {"n": 0, "edges": []}

    if n == 1:
        # Source is yes; the triangle is the smallest yes-instance of the
        # target problem.
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # n >= 2: add a universal vertex n.
    new_edges = [[u, v] for u, v in edges]
    for v in range(n):
        new_edges.append([n, v])
    return {"n": n + 1, "edges": new_edges}
