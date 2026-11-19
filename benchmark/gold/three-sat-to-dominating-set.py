"""Gold reduction: 3-SAT -> Dominating Set.              [test, less common]

SOURCE  3-SAT           {"num_vars": m, "clauses": [[l1, l2, l3], ...]}  yes iff satisfiable
TARGET  Dominating Set  {"n", "edges", "k"}  yes iff a dominating set of AT MOST k

Construction:
  * For each variable v a triangle: T_v (v true), F_v (v false), A_v.
    Numbered T_v = 3(v-1), F_v = 3(v-1) + 1, A_v = 3(v-1) + 2.
  * For each clause j a vertex C_j = 3m + j, joined to the literal vertex of
    each of its literals (T_v for +v, F_v for -v).
  k = m.

"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    edges = []
    for v in range(m):
        t, f, a = 3 * v, 3 * v + 1, 3 * v + 2
        edges += [[t, f], [t, a], [f, a]]
    for j, clause in enumerate(clauses):
        c = 3 * m + j
        for lit in clause:
            v = abs(lit) - 1
            edges.append([c, 3 * v if lit > 0 else 3 * v + 1])
    return {"n": 3 * m + len(clauses), "edges": edges, "k": m}