"""Polynomial-time reduction from 3-SAT to Dominating Set."""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Variable gadget: a triangle for each variable.
    # For variable i (1-indexed), vertices:
    #   3*(i-1)     : positive literal x_i
    #   3*(i-1) + 1 : negative literal ~x_i
    #   3*(i-1) + 2 : dummy vertex c_i (not connected to any clause)
    for i in range(1, m + 1):
        base = 3 * (i - 1)
        pos = base
        neg = base + 1
        dummy = base + 2
        edges.append([pos, neg])
        edges.append([pos, dummy])
        edges.append([neg, dummy])

    # Clause gadget: one vertex per clause, connected to the literal
    # vertices corresponding to the clause's literals.
    for j, clause in enumerate(clauses):
        clause_vertex = 3 * m + j
        for lit in clause:
            var = abs(lit)
            base = 3 * (var - 1)
            if lit > 0:
                edges.append([clause_vertex, base])
            else:
                edges.append([clause_vertex, base + 1])

    n = 3 * m + len(clauses)
    k = m

    return {"n": n, "edges": edges, "k": k}
