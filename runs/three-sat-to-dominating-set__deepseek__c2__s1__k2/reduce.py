def reduce(instance):
    """
    Polynomial-time reduction from 3-SAT to Dominating Set.

    For each variable v (1-indexed), create a triangle on vertices:
        T_v = 3*(v-1)      (literal v is true)
        F_v = 3*(v-1) + 1  (literal v is false)
        M_v = 3*(v-1) + 2  (middle vertex)

    The middle vertex M_v has neighbours exactly T_v and F_v, so every
    dominating set must contain at least one vertex from each variable
    gadget.  Hence at least m vertices are needed.  If exactly m are used,
    the chosen vertex in each gadget can be assumed to be T_v or F_v
    (replacing M_v by T_v never hurts domination), which defines a truth
    assignment.

    For each clause create one vertex connected to the three literal
    vertices corresponding to its literals.  With only m vertices in the
    dominating set (one per variable and no clause vertices), each clause
    vertex must be dominated by a selected literal vertex, i.e. the
    assignment satisfies the clause.

    Set k = m.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Variable gadgets: disjoint triangles.
    for v in range(1, m + 1):
        base = 3 * (v - 1)
        t = base
        f = base + 1
        mid = base + 2
        edges.append([t, f])
        edges.append([t, mid])
        edges.append([f, mid])

    # Clause vertices come after all variable-gadget vertices.
    clause_start = 3 * m
    for j, clause in enumerate(clauses):
        c = clause_start + j
        for lit in clause:
            v = abs(lit)
            base = 3 * (v - 1)
            if lit > 0:
                lit_vertex = base       # T_v
            else:
                lit_vertex = base + 1   # F_v
            edges.append([c, lit_vertex])

    return {
        "n": 3 * m + len(clauses),
        "edges": edges,
        "k": m,
    }
