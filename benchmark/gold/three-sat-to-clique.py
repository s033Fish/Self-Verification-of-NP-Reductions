"""Gold reduction: 3-SAT -> Clique.                      [test, famous]

SOURCE  3-SAT   {"num_vars": m, "clauses": [[l1, l2, l3], ...]}  yes iff satisfiable
TARGET  Clique  {"n", "edges", "k"}  yes iff a clique of AT LEAST k

Construction (Karp): one vertex per literal occurrence (clause j, position p
is vertex 3j + p). Join two occurrences when they are in DIFFERENT clauses
and are not complementary (not v and -v). k = number of clauses.
"""


def reduce(instance):
    clauses = instance["clauses"]
    occurrences = [(3 * j + p, j, lit) for j, clause in enumerate(clauses) for p, lit in enumerate(clause)]
    edges = [
        [u, v]
        for i, (u, cu, lu) in enumerate(occurrences)
        for (v, cv, lv) in occurrences[i + 1:]
        if cu != cv and lu != -lv
    ]
    return {"n": 3 * len(clauses), "edges": edges, "k": len(clauses)}