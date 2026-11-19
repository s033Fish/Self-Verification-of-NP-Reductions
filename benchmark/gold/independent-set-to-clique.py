"""Gold reduction: Independent Set -> Clique.            [test, famous]

SOURCE  Independent Set  {"n", "edges", "k"}  yes iff an independent set of AT LEAST k
TARGET  Clique           {"n", "edges", "k"}  yes iff a clique of AT LEAST k

"""


def reduce(instance):
    n = instance["n"]
    present = {frozenset(e) for e in instance["edges"]}
    edges = [[u, v] for u in range(n) for v in range(u + 1, n) if frozenset((u, v)) not in present]
    return {"n": n, "edges": edges, "k": instance["k"]}