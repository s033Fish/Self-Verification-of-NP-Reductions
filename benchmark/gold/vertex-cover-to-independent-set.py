"""Gold reduction: Vertex Cover -> Independent Set.     [test, famous]

SOURCE  Vertex Cover     {"n", "edges", "k"}  yes iff a cover of AT MOST k vertices
TARGET  Independent Set  {"n", "edges", "k"}  yes iff an independent set of AT LEAST k

Construction: the same graph, with k' = n - k.
"""


def reduce(instance):
    n = instance["n"]
    return {"n": n, "edges": [list(e) for e in instance["edges"]], "k": n - instance["k"]}