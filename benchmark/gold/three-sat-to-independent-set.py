"""Gold reduction: 3-SAT -> Independent Set.             [test, famous]

SOURCE  3-SAT            {"num_vars": m, "clauses": [[l1, l2, l3], ...]}  yes iff satisfiable
TARGET  Independent Set  {"n", "edges", "k"}  yes iff an independent set of AT LEAST k

Construction: one vertex per literal occurrence (clause j, position p is
vertex 3j + p).
  * A triangle on each clause's three vertices.
  * An edge between every two occurrences of complementary literals (v, -v).
  k = number of clauses.
"""


def reduce(instance):
    clauses = instance["clauses"]
    edges = []
    for j in range(len(clauses)):
        a, b, c = 3 * j, 3 * j + 1, 3 * j + 2
        edges += [[a, b], [a, c], [b, c]]
    occurrences = [(3 * j + p, lit) for j, clause in enumerate(clauses) for p, lit in enumerate(clause)]
    by_literal = {}
    for vertex, lit in occurrences:
        by_literal.setdefault(lit, []).append(vertex)
    for vertex, lit in occurrences:
        if lit > 0:
            edges += [[vertex, other] for other in by_literal.get(-lit, [])]
    return {"n": 3 * len(clauses), "edges": edges, "k": len(clauses)}