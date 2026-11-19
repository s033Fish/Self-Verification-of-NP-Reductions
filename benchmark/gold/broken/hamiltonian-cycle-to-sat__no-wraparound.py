"""BROKEN: Hamiltonian Cycle -> SAT without the last-to-first adjacency.

SOURCE  Hamiltonian Cycle  {"n", "edges"}  yes iff a cycle through every vertex
TARGET  SAT                {"num_vars", "clauses"}  yes iff satisfiable

Construction (position encoding): variable x(v, i) = v*n + i + 1 means
"vertex v is the i-th vertex of the cycle", for positions i = 0..n-1.
  * Every position holds exactly one vertex; every vertex is at exactly one
    position.
  * For consecutive positions i, i+1 AND the wrap-around pair (n-1, 0), and
    every ordered pair u != v that is NOT an edge: (-x(u, i) or -x(v, j)).
"""


def reduce(instance):
    n = instance["n"]
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}  # n <= 2: no simple cycle
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
    steps = [(i, i + 1) for i in range(n - 1)]  # BUG: this is Hamiltonian Path
    for i, j in steps:  # consecutive positions hold adjacent vertices
        for u in range(n):
            for v in range(n):
                if u != v and frozenset((u, v)) not in adjacent:
                    clauses.append([-x(u, i), -x(v, j)])
    return {"num_vars": n * n, "clauses": clauses}