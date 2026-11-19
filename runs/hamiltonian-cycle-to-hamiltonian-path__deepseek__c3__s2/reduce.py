"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Given an undirected graph G on vertices 0..n-1, we build a graph G' that has
a Hamiltonian path if and only if G has a Hamiltonian cycle.

Construction (for n >= 3):

  * Replace vertex 0 by two copies v' and v'' (vertices n-1 and n).
  * Every edge {0, u} of G becomes the two edges {v', u} and {v'', u}.
  * Every edge {u, w} with u, w != 0 stays as {u, w}.
  * Add two fresh pendant vertices a = n+1 and b = n+2 with the single
    edges {a, v'} and {b, v''}.

Correctness:

  (=>) A Hamiltonian cycle 0, u_1, ..., u_{n-1}, 0 of G becomes the
  Hamiltonian path a, v', u_1, ..., u_{n-1}, v'', b of G' (the two copies
  of vertex 0 are the two ends of the path, each attached to its pendant).

  (<=) In G', the pendant vertices a and b have degree 1, so any
  Hamiltonian path must start at one of them and end at the other, and
  hence must use the edges {a, v'} and {b, v''}. Removing a and b from
  the path leaves a Hamiltonian path of G' - {a, b} whose endpoints are
  v' and v''. Contracting v' and v'' back into a single vertex 0 turns
  that path into a Hamiltonian cycle of G (the two edges incident to v'
  and v'' become the two cycle edges at 0).

For n <= 2 the source answer is always no; we return the no-instance
{"n": 0, "edges": []} of Hamiltonian Path.

The construction runs in O(n + m) time, hence polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Hamiltonian Cycle is always no for n <= 2.
    if n <= 2:
        return {"n": 0, "edges": []}

    vp = n - 1   # first copy of vertex 0
    vpp = n      # second copy of vertex 0
    a = n + 1    # pendant attached to vp
    b = n + 2    # pendant attached to vpp

    new_edges = []
    for u, v in edges:
        if u == 0:
            u, v = v, u
        if v == 0:
            # edge {0, u} -> {vp, u-1} and {vpp, u-1}
            new_edges.append([vp, u - 1])
            new_edges.append([vpp, u - 1])
        else:
            new_edges.append([u - 1, v - 1])

    new_edges.append([a, vp])
    new_edges.append([b, vpp])

    return {"n": n + 3, "edges": new_edges}
