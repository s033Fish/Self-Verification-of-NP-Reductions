"""BROKEN: Hamiltonian Cycle -> Hamiltonian Path that splits vertex 0 without pendants.

SOURCE  Hamiltonian Cycle  {"n", "edges"}  yes iff a cycle through every vertex
TARGET  Hamiltonian Path   {"n", "edges"}  yes iff a path through every vertex (any ends)

Construction (n >= 3): split vertex 0.
  * Keep the graph. Add 0' = n, joined to every neighbour of 0.
  * Add pendant s = n + 1 joined only to 0, and pendant t = n + 2 joined only
    to 0'.
"""


def reduce(instance):
    n = instance["n"]
    if n <= 2:
        return {"n": 0, "edges": []}
    edges = [list(e) for e in instance["edges"]]
    split, s, t = n, n + 1, n + 2
    for u, v in instance["edges"]:
        if u == 0:
            edges.append([split, v])
        elif v == 0:
            edges.append([split, u])
    return {"n": n + 1, "edges": edges}  # BUG: without pendants the path may end anywhere