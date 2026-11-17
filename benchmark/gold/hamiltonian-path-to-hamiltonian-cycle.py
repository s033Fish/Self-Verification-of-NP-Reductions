"""Gold reduction: Hamiltonian Path -> Hamiltonian Cycle.     [difficulty: 3 of 6]

SOURCE  Hamiltonian Path   {"n": n, "edges": [[u, v], ...]}
        yes iff some path visits every vertex exactly once (any endpoints).
        n = 0 is no; n = 1 is yes.
TARGET  Hamiltonian Cycle  {"n": n, "edges": [[u, v], ...]}
        yes iff some cycle visits every vertex exactly once.
        Graphs with n <= 2 are always no.

Construction (n >= 2)
  1. Add one new vertex, numbered n, joined to every original vertex.
  2. A Hamiltonian path a -> ... -> b in G closes into a cycle through the
     new vertex: a -> ... -> b -> n -> a.
  3. Conversely, deleting the new vertex from a Hamiltonian cycle leaves a
     Hamiltonian path of G.
  So: n + 1 vertices, the original edges plus [i, n] for every i < n.

"""


def reduce(instance):
    n = instance["n"]
    edges = list(instance["edges"])

    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}


    for i in range(n):
        edges.append([i, n])

    return {"n": n+1, "edges": edges}