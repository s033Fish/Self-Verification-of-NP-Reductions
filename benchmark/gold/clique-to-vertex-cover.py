"""Gold reduction: Clique -> Vertex Cover.               [test, famous]

SOURCE  Clique        {"n", "edges", "k"}  yes iff a clique of AT LEAST k
TARGET  Vertex Cover  {"n", "edges", "k"}  yes iff a cover of AT MOST k

Construction: the complement graph, with k' = n - k.
"""


def reduce(instance):
    n = instance["n"]
    present = {frozenset(e) for e in instance["edges"]}
    edges = [[u, v] for u in range(n) for v in range(u + 1, n) if frozenset((u, v)) not in present]
    return {"n": n, "edges": edges, "k": n - instance["k"]}