import itertools

def reduce(instance):
    """Reduce a 3-SAT instance to a Vertex Cover instance.
    The reduction creates two vertices for each variable (true and false) connected by an edge.
    For each clause, it creates a triangle of three vertices, each linked to the corresponding
    literal vertex of the variable. The target k is set to m + 2*|clauses|.
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    # Variable vertices: for variable i (1-indexed), true vertex = 2*(i-1), false = 2*(i-1)+1
    var_true = lambda v: 2 * (v - 1)
    var_false = lambda v: 2 * (v - 1) + 1
    edges = []
    # edges between true/false of each variable
    for v in range(1, m + 1):
        edges.append([var_true(v), var_false(v)])
    # clause literal vertices start after variable vertices
    base = 2 * m
    clause_vertices = []  # list of lists of three vertex ids per clause
    for idx, clause in enumerate(clauses):
        # clause has exactly three literals
        lit_vertices = []
        for t in range(3):
            lit_vertices.append(base + 3 * idx + t)
        clause_vertices.append(lit_vertices)
        # triangle edges among the three clause vertices
        a, b, c = lit_vertices
        edges.append([a, b])
        edges.append([b, c])
        edges.append([c, a])
        # connect each clause vertex to its literal's variable vertex
        for lit, cv in zip(clause, lit_vertices):
            sign = lit[0]
            var = int(lit[1:])
            if sign == '+':
                edges.append([cv, var_true(var)])
            elif sign == '-':
                edges.append([cv, var_false(var)])
            else:
                raise ValueError(f"Invalid literal format: {lit}")
    n = base + 3 * len(clauses)
    k = m + 2 * len(clauses)
    # Ensure edges are undirected and no self-loops; also order vertices consistently
    clean_edges = []
    seen = set()
    for u, v in edges:
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in seen:
            seen.add((a, b))
            clean_edges.append([a, b])
    return {"n": n, "edges": clean_edges, "k": k}

# If this file is run directly, perform a simple self-test (optional)
if __name__ == "__main__":
    # Example: (x1 ∨ ¬x2 ∨ x3)
    example = {"num_vars": 3, "clauses": [["+1", "-2", "+3"]]}
    vc = reduce(example)
    print(vc)
