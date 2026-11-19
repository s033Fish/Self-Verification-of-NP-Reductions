def reduce(instance):
    """Reduce a 3-SAT instance to a Vertex Cover instance.

    Source instance format:
        {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

    Target instance format:
        {"n": n, "edges": [[u, v], ...], "k": k}

    Construction:
      * For each variable v, add an edge between vertices +v and -v.
      * For each clause, add a triangle on three fresh vertices, one per
        literal in the clause.
      * Connect each clause-literal vertex to the variable vertex for the
        opposite literal.
      * Set k = m + 2 * (number of clauses).
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    c = len(clauses)

    def pos_vertex(v):
        # Vertex representing literal +v.
        return 2 * (v - 1)

    def neg_vertex(v):
        # Vertex representing literal -v.
        return 2 * (v - 1) + 1

    edges = []

    # Variable gadgets: one edge per variable.
    for v in range(1, m + 1):
        edges.append([pos_vertex(v), neg_vertex(v)])

    # Clause gadgets: one triangle per clause, plus cross edges.
    next_vertex = 2 * m
    for clause in clauses:
        c0 = next_vertex
        c1 = next_vertex + 1
        c2 = next_vertex + 2
        next_vertex += 3

        # Triangle among the three clause-literal vertices.
        edges.append([c0, c1])
        edges.append([c1, c2])
        edges.append([c0, c2])

        # Cross edges to the opposite literal's variable vertex.
        for clause_vertex, lit in zip((c0, c1, c2), clause):
            if lit > 0:
                opposite = neg_vertex(lit)
            else:
                opposite = pos_vertex(-lit)
            edges.append([clause_vertex, opposite])

    n = next_vertex
    k = m + 2 * c
    return {"n": n, "edges": edges, "k": k}
