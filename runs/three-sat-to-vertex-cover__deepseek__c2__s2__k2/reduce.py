def reduce(instance):
    """
    Polynomial-time reduction from 3-SAT to Vertex Cover.

    Source instance:
        {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Target instance:
        {"n": n, "edges": [[u, v], ...], "k": k}

    Construction:
      * For each variable i (1..m), create vertices 2*(i-1) and 2*(i-1)+1
        representing +i and -i, joined by an edge.
      * For each clause j, create three new vertices forming a triangle.
      * Connect each clause vertex to the variable vertex representing its
        literal.
      * Set k = m + 2*c, where c is the number of clauses.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    c = len(clauses)

    n = 2 * m + 3 * c
    edges = []

    # Variable gadgets: one edge per variable, connecting +i and -i.
    for i in range(m):
        edges.append([2 * i, 2 * i + 1])

    # Clause gadgets: a triangle of three fresh vertices per clause,
    # with one edge from each triangle vertex to its literal's vertex.
    for j, clause in enumerate(clauses):
        base = 2 * m + 3 * j

        # Triangle among the three clause vertices.
        edges.append([base, base + 1])
        edges.append([base + 1, base + 2])
        edges.append([base, base + 2])

        # Connect each clause vertex to the vertex of its literal.
        for offset, lit in enumerate(clause):
            if lit > 0:
                lit_vertex = 2 * (lit - 1)
            else:
                lit_vertex = 2 * (-lit - 1) + 1
            edges.append([base + offset, lit_vertex])

    k = m + 2 * c
    return {"n": n, "edges": edges, "k": k}
