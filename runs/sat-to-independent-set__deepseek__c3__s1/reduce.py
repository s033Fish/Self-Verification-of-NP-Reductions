"""Polynomial-time reduction from SAT to Independent Set.

Construction (standard):
  * For every clause C, add a clique with one vertex per literal occurrence
    in C (so a clause with t literals contributes t vertices, pairwise joined).
  * For every variable v, join every vertex whose literal is +v to every
    vertex whose literal is -v (consistency edges).
  * Set k = number of clauses.

A satisfying assignment yields an independent set of size (#clauses) by
picking, in each clause, one vertex whose literal is true.  Conversely, any
independent set of size (#clauses) must pick exactly one vertex per clause
clique; the consistency edges guarantee the chosen literals are jointly
satisfiable, so the formula is satisfiable.

An empty clause contributes no vertex, so at most (#clauses - 1) vertices can
be chosen, correctly making the instance no.

Note: a clause may contain both v and -v, or repeat a literal.  The clique
edge and the consistency edge can then coincide, so edges are deduplicated.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = set()
    n = 0

    # Map each variable to the list of vertices carrying +v and -v.
    positive = {v: [] for v in range(1, num_vars + 1)}
    negative = {v: [] for v in range(1, num_vars + 1)}

    for clause in clauses:
        clique = []
        for literal in clause:
            vertex = n
            n += 1
            clique.append(vertex)
            if literal > 0:
                positive[literal].append(vertex)
            else:
                negative[-literal].append(vertex)
        # Clique edges inside the clause.
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                edges.add((clique[i], clique[j]))

    # Consistency edges between +v and -v occurrences.
    for v in range(1, num_vars + 1):
        for u in positive[v]:
            for w in negative[v]:
                edges.add((u, w) if u < w else (w, u))

    return {"n": n, "edges": [[u, v] for u, v in edges], "k": len(clauses)}
