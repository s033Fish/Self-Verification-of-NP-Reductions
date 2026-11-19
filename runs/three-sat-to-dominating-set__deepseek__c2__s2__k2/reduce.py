def reduce(instance):
    """
    Polynomial-time reduction from 3-SAT to Dominating Set.

    Source instance format:
        {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Target instance format:
        {"n": n, "edges": [[u, v], ...], "k": k}

    Construction:
      * For each variable v in 1..m, create a triangle on vertices
            T_v = 3*(v-1), F_v = 3*(v-1)+1, A_v = 3*(v-1)+2.
        Every dominating set must contain at least one vertex of this
        triangle.  If it contains exactly one, that vertex represents the
        variable's truth value; A_v is auxiliary and is not connected to any
        clause.
      * For each clause j, create one vertex C_j = 3*m + j and connect it to
        the three variable vertices corresponding to its literals.
      * Set k = m.

    If the formula is satisfiable, choose T_v or F_v according to the
    assignment.  This is a dominating set of size m.  Conversely, a dominating
    set of size m must choose exactly one vertex in each variable triangle and
    no clause vertex; each clause vertex is then adjacent to a chosen variable
    vertex, which gives a satisfying assignment.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Variable triangles.
    for v in range(1, m + 1):
        base = 3 * (v - 1)
        t, f, a = base, base + 1, base + 2
        edges.append([t, f])
        edges.append([t, a])
        edges.append([f, a])

    # Clause vertices and their incident edges.
    for j, clause in enumerate(clauses):
        c = 3 * m + j
        for lit in clause:
            if lit > 0:
                var_vertex = 3 * (lit - 1)
            else:
                var_vertex = 3 * ((-lit) - 1) + 1
            edges.append([c, var_vertex])

    n = 3 * m + len(clauses)
    return {"n": n, "edges": edges, "k": m}
