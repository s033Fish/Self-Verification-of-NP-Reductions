"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Source instance: {"n": n, "edges": [[u, v], ...]}  (undirected simple graph)
Target instance: {"n": n, "edges": [[u, v], ...]}  (undirected simple graph)

Idea
----
For n <= 2 the source is always a "no" instance, so we return a trivially
"no" target instance ({"n": 0, "edges": []}).

For n >= 3, pick vertex v = 0.  Let H = G - 0 and let S = N_G(0) be the
neighbours of 0.  Build G' by adding four new vertices s, t, y, z:

  * keep every edge of H,
  * connect s to every vertex of S,
  * connect t to every vertex of S,
  * add the edge s-y,
  * add the edge t-z.

The vertices y and z are leaves, so in any Hamiltonian path of G' they
must be the two endpoints.  Hence such a path has the form

      y - s - a - ... - b - t - z

with a, b in S, and the middle part a - ... - b is a Hamiltonian path of
H whose endpoints are neighbours of 0.  Adding 0 closes that path into a
Hamiltonian cycle of G (and conversely, breaking a Hamiltonian cycle of G
at 0 yields such a path).  Therefore G' has a Hamiltonian path iff G has a
Hamiltonian cycle.

The construction uses O(n + m) time and adds only 4 vertices, so it is a
polynomial-time (indeed linear-time) reduction.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: Hamiltonian Cycle is always false.
    if n <= 2:
        return {"n": 0, "edges": []}

    # New vertices.
    s = n
    t = n + 1
    y = n + 2
    z = n + 3

    new_edges = []
    neighbours_of_0 = []

    for u, v in edges:
        if u == 0:
            neighbours_of_0.append(v)
        elif v == 0:
            neighbours_of_0.append(u)
        else:
            new_edges.append([u, v])

    for u in neighbours_of_0:
        new_edges.append([s, u])
        new_edges.append([t, u])

    new_edges.append([s, y])
    new_edges.append([t, z])

    return {"n": n + 4, "edges": new_edges}
