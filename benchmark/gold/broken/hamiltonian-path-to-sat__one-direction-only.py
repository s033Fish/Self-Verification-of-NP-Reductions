"""BROKEN: Hamiltonian Path -> SAT that forbids non-edges in one direction only.

SOURCE  Hamiltonian Path  {"n", "edges"}  yes iff a path through every vertex (any ends)
TARGET  SAT               {"num_vars", "clauses"}  yes iff satisfiable

Construction (position encoding): variable x(v, i) = v*n + i + 1 means
"vertex v is the i-th vertex of the path", for positions i = 0..n-1.
  * Every position holds exactly one vertex; every vertex is at exactly one
    position (at-least-one clauses plus pairwise at-most-one clauses).
  * For positions i, i+1 and every ordered pair u != v that is NOT an edge:
    (-x(u, i) or -x(v, i+1)).
"""


def reduce(instance):
    n = instance["n"]
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}  # n = 0: no path
    adjacent = {frozenset(e) for e in instance["edges"]}

    def x(v, i):  # vertex v is at position i
        return v * n + i + 1

    clauses = []
    for i in range(n):  # every position holds exactly one vertex
        clauses.append([x(v, i) for v in range(n)])
        clauses.extend([-x(u, i), -x(v, i)] for u in range(n) for v in range(u + 1, n))
    for v in range(n):  # every vertex is at exactly one position
        clauses.append([x(v, i) for i in range(n)])
        clauses.extend([-x(v, i), -x(v, j)] for i in range(n) for j in range(i + 1, n))
    steps = [(i, i + 1) for i in range(n - 1)]
    for i, j in steps:  # consecutive positions hold adjacent vertices
        for u in range(n):
            for v in range(u + 1, n):  # BUG: v-then-u is never checked
                if u != v and frozenset((u, v)) not in adjacent:
                    clauses.append([-x(u, i), -x(v, j)])
    return {"num_vars": n * n, "clauses": clauses}