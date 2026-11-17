"""Broken: variables numbered from 0, but SAT variables start at 1.

Vertex 0 with colour 0 becomes variable 0, and literal 0 is invalid.
Expect malformed_output on a single vertex.
"""


def reduce(instance):
    n = instance["n"]
    clauses = [[3 * i, 3 * i + 1, 3 * i + 2] for i in range(n)]
    for i, j in instance["edges"]:
        for c in range(3):
            clauses.append([-(3 * i + c), -(3 * j + c)])
    return {"num_vars": 3 * n, "clauses": clauses}