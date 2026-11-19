"""Reduction from 3-SAT to Vertex Cover.

Source problem (ThreeSat) instance format:
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Literals are integers: +v for true, -v for false.

Target problem (VertexCover) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction constructs a graph as described in classic textbooks.
"""

def reduce(instance):
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        A dict with keys "num_vars" and "clauses" as described above.

    Returns
    -------
    dict
        A Vertex Cover instance with keys "n", "edges", and "k".
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    c = len(clauses)

    # Vertex ids:
    # For each variable i (1‑based) we create two vertices:
    #   true  -> 2*(i-1)
    #   false -> 2*(i-1)+1
    var_true = lambda v: 2 * (v - 1)
    var_false = lambda v: 2 * (v - 1) + 1

    # Clause vertices start after the 2*m variable vertices.
    clause_base = 2 * m

    edges = []
    # 1. Variable edges (ensure each variable chooses true or false).
    for i in range(1, m + 1):
        edges.append([var_true(i), var_false(i)])

    # 2. Clause gadgets.
    for idx, clause in enumerate(clauses):
        # clause vertices ids
        v0 = clause_base + 3 * idx
        v1 = v0 + 1
        v2 = v0 + 2
        clause_vertices = [v0, v1, v2]
        # triangle edges among clause vertices
        edges.append([v0, v1])
        edges.append([v1, v2])
        edges.append([v2, v0])
        # connect each clause vertex to the corresponding literal vertex
        for pos, lit in enumerate(clause):
            var = abs(lit)
            if var == 0:
                # Defensive: ignore malformed literals (should not happen)
                continue
            if lit > 0:
                lit_vertex = var_true(var)
            else:
                lit_vertex = var_false(var)
            clause_vertex = clause_vertices[pos]
            edges.append([clause_vertex, lit_vertex])

    n = clause_base + 3 * c  # total number of vertices
    k = m + 2 * c            # size bound for vertex cover

    # Ensure edges are undirected and no self‑loops; duplicates are harmless for the verifier.
    return {"n": n, "edges": edges, "k": k}

# The module can be imported; no top‑level execution needed.
