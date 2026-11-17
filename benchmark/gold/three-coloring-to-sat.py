"""Gold reduction: 3-Coloring -> SAT.                [difficulty: 4 of 6]

SOURCE  3-Coloring  {"n": n, "edges": [[u, v], ...]}
        yes iff each vertex can get one of 3 colours with every edge's
        endpoints coloured differently.
TARGET  SAT         {"num_vars": m, "clauses": [[literal, ...], ...]}
        variables 1..m; literal +v / -v; any clause length.

Construction (a standard encoding)
  1. One variable per (vertex, colour): "vertex v has colour c", for
     v in 0..n-1 and c in 0..2. A simple numbering: var(v, c) = 3 * v + c + 1,
     so num_vars = 3 * n.
  2. Every vertex gets at least one colour:
       [var(v, 0), var(v, 1), var(v, 2)]                  for each vertex v
  3. Adjacent vertices never share a colour:
       [-var(u, c), -var(w, c)]                            for each edge [u, w]
                                                           and each colour c
"""

def var(v, c):
    return 3 * v + c + 1


def reduce(instance):
    n = instance["n"]
    edges = list(instance["edges"])

    num_vars = 3 * n
    clauses = []

    for i in range(n):
        clauses.append([var(i, 0), var(i, 1), var(i, 2)])

    for [i, j] in edges:
        clauses.append([-var(i, 0), -var(j, 0)])
        clauses.append([-var(i, 1), -var(j, 1)])
        clauses.append([-var(i, 2), -var(j, 2)])

    return {"num_vars": num_vars, "clauses": clauses}
