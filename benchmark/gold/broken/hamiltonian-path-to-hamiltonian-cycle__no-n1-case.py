"""Broken: no special case for n = 1.

One vertex has a Hamiltonian path (yes), but the construction gives two
vertices and one edge, which never has a Hamiltonian cycle (no).
Expect wrong_answer_yes_to_no on {"n": 1, "edges": []}.
"""


def reduce(instance):
    n = instance["n"]
    edges = list(instance["edges"])
    for i in range(n):
        edges.append([i, n])
    return {"n": n + 1, "edges": edges}