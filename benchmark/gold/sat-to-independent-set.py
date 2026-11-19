"""Gold reduction: SAT -> Independent Set.               [test, famous]

SOURCE  SAT              {"num_vars": m, "clauses": [[literal, ...], ...]}  any clause lengths
TARGET  Independent Set  {"n", "edges", "k"}  yes iff an independent set of AT LEAST k

Construction: one vertex per literal occurrence, numbered in order.
  * A clique on each clause's occurrences (at most one chosen per clause).
  * An edge between every two complementary occurrences (v and -v) in
    different clauses (inside a clause they are already joined).
  k = number of clauses.
"""


def reduce(instance):
    clauses = instance["clauses"]
    occurrences = [(j, lit) for j, clause in enumerate(clauses) for lit in clause]
    edges = [
        [u, v]
        for u, (cu, lu) in enumerate(occurrences)
        for v in range(u + 1, len(occurrences))
        if cu == occurrences[v][0] or lu == -occurrences[v][1]
    ]
    return {"n": len(occurrences), "edges": edges, "k": len(clauses)}