"""Reduction from 3-SAT to Vertex Cover.

The source problem (ThreeSat) instance format:
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Literals are signed integers: +v means variable v is true, -v means variable v is false.

The target problem (VertexCover) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
    Vertices are numbered 0..n-1.

The construction follows the classic polynomial‑time reduction:
    * For each variable i (1..m) create two vertices T_i and F_i (true/false).
      Add an edge (T_i, F_i).  In any vertex cover of size ≤ m+2|C| we will pick
      exactly one of the two, encoding the truth assignment.
    * For each clause C = (ℓ1, ℓ2, ℓ3) create three new vertices c1, c2, c3
      forming a triangle.  A triangle needs at least two vertices in any vertex
      cover, so we budget exactly 2 vertices per clause.
    * Connect each clause vertex c_p to the literal vertex that represents the
      literal ℓ_p (i.e., to T_v if ℓ_p = +v, otherwise to F_v).
    * Set k = m + 2·|clauses|.

Correctness sketch:
    * If the 3‑SAT formula is satisfiable, choose for each variable the vertex
      corresponding to the false literal if the variable is set true, and the
      true vertex otherwise.  This picks exactly one endpoint of each variable
      edge (m vertices).  For each clause, at least one literal is true, so the
      edge from the corresponding clause vertex to its literal vertex is already
      covered; we can cover the remaining two edges of the triangle by picking
      the other two clause vertices.  Thus we obtain a vertex cover of size
      m + 2·|clauses|.
    * Conversely, any vertex cover of size ≤ m + 2·|clauses| must contain at
      least one endpoint of each variable edge, and cannot afford both
      endpoints (that would exceed the budget).  Hence it selects exactly one
      literal per variable, defining a truth assignment.  For each clause, the
      triangle forces at least two of its three clause vertices into the cover.
      If all three clause vertices were chosen, we would exceed the budget, so
      exactly two are chosen, meaning the third clause vertex is not in the
      cover.  The edge from that third vertex to its literal must therefore be
      covered by the literal vertex, implying that literal is true under the
      assignment.  Hence each clause has a satisfied literal.

Thus the reduction is correct and runs in polynomial time.
"""

def reduce(instance):
    """Convert a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "num_vars" (int) and "clauses" (list of
        three‑element lists of ints).

    Returns
    -------
    dict
        A Vertex Cover instance with keys "n", "edges", and "k".
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    c = len(clauses)

    # Vertex numbering:
    #   true_i = 2*(i-1)
    #   false_i = 2*(i-1) + 1   for i in 1..m
    # Clause vertices start at base = 2*m, three per clause.
    base_clause = 2 * m
    n = 2 * m + 3 * c
    edges = []

    # Variable edges (T_i, F_i)
    for i in range(1, m + 1):
        t = 2 * (i - 1)
        f = t + 1
        edges.append([t, f])

    # Clause gadgets
    for j, clause in enumerate(clauses):
        # clause vertex ids
        a = base_clause + 3 * j
        b = a + 1
        d = a + 2
        # triangle edges
        edges.append([a, b])
        edges.append([b, d])
        edges.append([a, d])
        # connect each clause vertex to its literal vertex
        for p, lit in enumerate(clause):
            var = abs(lit)
            # literal vertex: true if lit>0 else false
            lit_vertex = 2 * (var - 1) if lit > 0 else 2 * (var - 1) + 1
            clause_vertex = base_clause + 3 * j + p
            # ensure smaller index first for consistency (not required)
            u, v = (lit_vertex, clause_vertex) if lit_vertex < clause_vertex else (clause_vertex, lit_vertex)
            edges.append([u, v])

    k = m + 2 * c
    return {"n": n, "edges": edges, "k": k}

if __name__ == "__main__":
    # Simple sanity test when run directly.
    import json, sys
    if len(sys.argv) != 2:
        print("Usage: python reduce.py <input_json_file>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        inst = json.load(f)
    out = reduce(inst)
    print(json.dumps(out, indent=2))

