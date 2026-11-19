"""Gold reduction: 3-Coloring -> Independent Set.        [test, less common]

SOURCE  3-Coloring       {"n", "edges"}       yes iff 3-colourable
TARGET  Independent Set  {"n", "edges", "k"}  yes iff an independent set of AT LEAST k

Construction: three copies of every vertex, (v, 0), (v, 1), (v, 2), one per
colour, numbered 3v + c.
  * A triangle on the three copies of each vertex: an independent set takes
    at most one colour per vertex.
  * For every source edge uv and colour c, an edge (u, c) - (v, c):
    neighbours cannot take the same colour.
  k = n.
"""


def reduce(instance):
    n = instance["n"]
    edges = []
    for v in range(n):
        a, b, c = 3 * v, 3 * v + 1, 3 * v + 2
        edges += [[a, b], [a, c], [b, c]]
    for u, v in instance["edges"]:
        for colour in range(3):
            edges.append([3 * u + colour, 3 * v + colour])
    return {"n": 3 * n, "edges": edges, "k": n}