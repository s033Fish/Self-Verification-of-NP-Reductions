"""BROKEN: SAT -> Clique that ignores empty clauses.

SOURCE  SAT     {"num_vars": m, "clauses": [[literal, ...], ...]}  any clause lengths
TARGET  Clique  {"n", "edges", "k"}  yes iff a clique of AT LEAST k

Construction (Karp): one vertex per literal occurrence, numbered in order.
Join two occurrences when they are in DIFFERENT clauses and are not
complementary (not v and -v). k = number of clauses.
"""


def reduce(instance):
    clauses = instance["clauses"]
    occurrences = [(j, lit) for j, clause in enumerate(clauses) for lit in clause]
    edges = [
        [u, v]
        for u, (cu, lu) in enumerate(occurrences)
        for v in range(u + 1, len(occurrences))
        if cu != occurrences[v][0] and lu != -occurrences[v][1]
    ]
    return {"n": len(occurrences), "edges": edges, "k": sum(1 for c in clauses if c)}  # BUG: empty clauses make it no