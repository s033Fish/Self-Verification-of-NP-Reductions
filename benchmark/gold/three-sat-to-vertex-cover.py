"""Gold reduction: 3-SAT -> Vertex Cover.                [test, famous]

SOURCE  3-SAT         {"num_vars": m, "clauses": [[l1, l2, l3], ...]}  yes iff satisfiable
TARGET  Vertex Cover  {"n", "edges", "k"}  yes iff a cover of AT MOST k

Construction: the 3-SAT -> Independent Set graph (a triangle per clause on
its three literal occurrences, plus an edge between every two complementary
occurrences), with k = 2c, where c = number of clauses.
"""


def reduce(instance):
    clauses = instance["clauses"]
    edges = []
    for j in range(len(clauses)):
        a, b, c = 3 * j, 3 * j + 1, 3 * j + 2
        edges += [[a, b], [a, c], [b, c]]
    by_literal = {}
    for j, clause in enumerate(clauses):
        for p, lit in enumerate(clause):
            by_literal.setdefault(lit, []).append(3 * j + p)
    for lit, vertices in by_literal.items():
        if lit > 0:
            edges += [[u, w] for u in vertices for w in by_literal.get(-lit, [])]
    return {"n": 3 * len(clauses), "edges": edges, "k": 2 * len(clauses)}