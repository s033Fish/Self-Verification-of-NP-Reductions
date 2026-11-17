"""Broken: looks edges up as ordered pairs, so an input edge listed as [v, u]
is not recognised as the pair (u, v). Only the verifier's shuffled instances
reverse edges, so this passes every sorted instance and is caught in the
random phase. Expect a wrong_answer category.
"""


def reduce(instance):
    n = instance["n"]
    present = {tuple(edge) for edge in instance["edges"]}  # should be frozenset
    complement = [[u, v] for u in range(n) for v in range(u + 1, n) if (u, v) not in present]
    return {"n": n, "edges": complement, "k": instance["k"]}