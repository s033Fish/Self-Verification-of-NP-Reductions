"""Polynomial-time reduction from SAT (CNF satisfiability) to Independent Set.

Construction (the standard one):

  * Create one vertex for every occurrence of a literal in the formula
    (occurrences are counted separately, so repeated literals in a clause
    become distinct vertices).
  * For every clause, add edges making its literal-occurrence vertices a
    clique.  Hence an independent set contains at most one vertex per
    clause.
  * For every variable v, add an edge between every occurrence of literal
    +v and every occurrence of literal -v.  Hence an independent set cannot
    choose both a variable and its negation.
  * Set k = number of clauses.

Correctness:
  * If the formula is satisfiable, pick in each clause one true literal;
    the corresponding vertices form an independent set of size (#clauses):
    at most one per clause clique, and no contradictory pair because the
    assignment is consistent.
  * Conversely, an independent set of size >= (#clauses) must pick exactly
    one vertex from each clause clique (the cliques partition the vertices,
    and each contributes at most one).  Assign each variable true if a
    chosen +v vertex exists, false if a chosen -v vertex exists; the
    consistency edges guarantee this is well defined.  Every clause then
    contains a true literal.

Edge cases:
  * No clauses -> k = 0 and an empty graph, which is yes (k <= 0).
  * An empty clause -> its clique has no vertices, so the maximum
    independent set has size at most (#clauses - 1) < k, giving no.
  * Variables that never occur simply contribute no vertices.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Assign a vertex id to every literal occurrence.
    clause_vertices = []          # clause index -> list of vertex ids
    literal_occurrences = {}      # literal -> list of vertex ids
    next_id = 0

    for clause in clauses:
        vs = []
        for literal in clause:
            vs.append(next_id)
            literal_occurrences.setdefault(literal, []).append(next_id)
            next_id += 1
        clause_vertices.append(vs)

    n = next_id
    edge_set = set()

    def add_edge(u, v):
        if u != v:
            edge_set.add(frozenset((u, v)))

    # Clique on the literal occurrences of each clause.
    for vs in clause_vertices:
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                add_edge(vs[i], vs[j])

    # Consistency edges between complementary literals.
    for literal, occurrences in literal_occurrences.items():
        if literal > 0:
            complementary = literal_occurrences.get(-literal)
            if complementary:
                for u in occurrences:
                    for v in complementary:
                        add_edge(u, v)

    edges = [list(edge) for edge in edge_set]
    return {"n": n, "edges": edges, "k": len(clauses)}
