"""Gold reduction: NAE-3-SAT -> 3-Coloring.              [test, less common]

SOURCE  NAE-3-SAT   {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
                    yes iff some assignment gives every clause a true AND a false literal
TARGET  3-Coloring  {"n", "edges"}  yes iff 3-colourable

Construction:
  * A base vertex N = 0.
  * For each variable v, vertices P_v = 2v - 1 (literal +v) and Q_v = 2v
    (literal -v), in a triangle with N. So every literal vertex avoids N's
    colour, and +v, -v take the two other colours: call them true and false.
  * For each clause j, a triangle t_j1, t_j2, t_j3, with t_jk joined to the
    vertex of the clause's k-th literal.
"""


def reduce(instance):
    m, clauses = instance["num_vars"], instance["clauses"]
    edges = []
    for v in range(1, m + 1):
        p, q = 2 * v - 1, 2 * v
        edges += [[0, p], [0, q], [p, q]]

    def vertex(lit):
        return 2 * lit - 1 if lit > 0 else 2 * (-lit)

    n = 2 * m + 1
    for clause in clauses:
        t = [n, n + 1, n + 2]
        n += 3
        edges += [[t[0], t[1]], [t[0], t[2]], [t[1], t[2]]]
        edges += [[t[k], vertex(lit)] for k, lit in enumerate(clause)]
    return {"n": n, "edges": edges}