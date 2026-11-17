"""Polynomial-time reduction from 3-Coloring to SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction (standard):
  For every vertex v in 0..n-1 and colour c in {0, 1, 2} introduce the
  variable x(v, c) = 3*v + c + 1, meaning "vertex v has colour c".

  Clauses:
    * For each vertex v: [x(v,0), x(v,1), x(v,2)]
        -> v gets at least one colour.
    * For each vertex v and each colour pair a < b:
        [-x(v,a), -x(v,b)]
        -> v gets at most one colour.
    * For each edge {u, v} and each colour c:
        [-x(u,c), -x(v,c)]
        -> the endpoints of an edge do not share a colour.

  A satisfying assignment of the CNF corresponds exactly to a proper
  3-colouring (choose for each vertex any colour whose variable is true),
  and conversely any proper 3-colouring satisfies all clauses.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    def var(v, c):
        return 3 * v + c + 1

    clauses = []

    # At least one colour per vertex.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # At most one colour per vertex.
    for v in range(n):
        clauses.append([-var(v, 0), -var(v, 1)])
        clauses.append([-var(v, 0), -var(v, 2)])
        clauses.append([-var(v, 1), -var(v, 2)])

    # Adjacent vertices must differ in colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": 3 * n, "clauses": clauses}
