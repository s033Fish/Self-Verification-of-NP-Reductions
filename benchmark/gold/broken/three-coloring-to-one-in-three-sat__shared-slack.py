"""Broken: one slack variable shared by every edge and colour.

A properly coloured edge always leaves one colour unused, whose clause needs
the slack true, while the two used colours need it false. So every graph with
an edge becomes unsatisfiable. Expect wrong_answer_yes_to_no on a single edge.
"""


def var(v, c):
    return 3 * v + c + 1


def reduce(instance):
    n = instance["n"]
    slack = 3 * n + 1
    clauses = [[var(i, 0), var(i, 1), var(i, 2)] for i in range(n)]
    for i, j in instance["edges"]:
        for c in range(3):
            clauses.append([var(i, c), var(j, c), slack])
    return {"num_vars": 3 * n + 1, "clauses": clauses}