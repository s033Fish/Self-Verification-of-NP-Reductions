"""Polynomial-time reduction from 3-SAT to Independent Set.

Construction
------------
For each variable v in 1..num_vars, create two vertices:
    true  vertex: 2*(v-1)
    false vertex: 2*(v-1) + 1
and add an edge between them, so an independent set cannot choose both
truth values of the same variable.

For each clause, create a triangle of three vertices, one for each
literal occurrence in that clause.  An independent set can therefore
choose at most one literal from each clause.

For a clause vertex representing literal l, add an edge to the variable
vertex representing the *opposite* truth value of l.  Thus choosing a
clause literal is compatible with the variable assignment exactly when
the literal is true under that assignment.

The formula is satisfiable iff the resulting graph has an independent
set of size num_vars + num_clauses: such a set must contain exactly one
vertex from each variable pair and exactly one vertex from each clause
triangle, and the cross edges enforce that the chosen literals are all
true under the assignment encoded by the variable-pair choices.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an Independent Set instance.

    Input format:
        {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

    Output format:
        {"n": n, "edges": [[u, v], ...], "k": k}
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []
    seen_edges = set()

    def add_edge(u, v):
        if u == v:
            return
        key = (u, v) if u < v else (v, u)
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append([u, v])

    # One true/false pair per variable.
    for v in range(1, num_vars + 1):
        true_vertex = 2 * (v - 1)
        false_vertex = true_vertex + 1
        add_edge(true_vertex, false_vertex)

    # One triangle per clause, plus conflict edges to variable vertices.
    clause_base = 2 * num_vars
    for clause_index, clause in enumerate(clauses):
        c0 = clause_base + 3 * clause_index
        c1 = c0 + 1
        c2 = c0 + 2

        # Triangle: at most one literal from this clause can be chosen.
        add_edge(c0, c1)
        add_edge(c0, c2)
        add_edge(c1, c2)

        for offset, literal in enumerate(clause):
            variable = abs(literal)
            if literal > 0:
                # Choosing +variable conflicts with variable being false.
                opposite_vertex = 2 * (variable - 1) + 1
            else:
                # Choosing -variable conflicts with variable being true.
                opposite_vertex = 2 * (variable - 1)
            add_edge(c0 + offset, opposite_vertex)

    n = clause_base + 3 * len(clauses)
    k = num_vars + len(clauses)

    return {"n": n, "edges": edges, "k": k}
