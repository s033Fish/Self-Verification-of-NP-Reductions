r"""Gold reduction: Independent Set -> Vertex Cover.

S is an independent set of G exactly when V \ S is a vertex cover of G, so
G has an independent set of at least k vertices iff it has a vertex cover of
at most n - k vertices. Same graph, new budget.
"""


def reduce(instance):
    n = instance["n"]
    return {"n": n, "edges": instance["edges"], "k": n - instance["k"]}