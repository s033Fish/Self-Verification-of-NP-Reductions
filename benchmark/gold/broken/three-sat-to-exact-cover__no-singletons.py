"""Broken: leaves out the singleton sets {P_{j,k}}.

A clause with two or three true literals then has a true occurrence that
nothing can cover exactly once. Expect wrong_answer_yes_to_no.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    c = len(clauses)
    occurrence = lambda j, k: m + c + 3 * j + k
    sets = []
    for v in range(1, m + 1):
        sets.append([v - 1] + [occurrence(j, k) for j, cl in enumerate(clauses) for k, l in enumerate(cl) if l == -v])
        sets.append([v - 1] + [occurrence(j, k) for j, cl in enumerate(clauses) for k, l in enumerate(cl) if l == v])
    for j in range(c):
        for k in range(3):
            sets.append([m + j, occurrence(j, k)])
    return {"universe_size": m + 4 * c, "sets": sets}