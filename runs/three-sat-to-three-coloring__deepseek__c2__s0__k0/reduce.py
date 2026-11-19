def reduce(instance):
    """
    Polynomial-time reduction from 3-SAT to 3-Coloring.

    Construction:
      * A base triangle B, T, F.
      * For each variable v, vertices pos_v and neg_v joined to each other
        and to B, forcing them to be the two colours T and F in opposite
        order.
      * For each clause, two OR gates compute the disjunction of the three
        literals.  The final OR output is forced to T by an edge to F.

    The OR gate is built from NOT and NAND gates.  The NAND gate has the
    crucial property that when both inputs are T, its output is forced to F;
    this makes an all-false clause uncolorable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    B, T, F = 0, 1, 2
    edges = [[B, T], [T, F], [F, B]]
    next_id = 3

    pos = {}
    neg = {}
    for v in range(1, m + 1):
        p = next_id
        next_id += 1
        n = next_id
        next_id += 1
        pos[v] = p
        neg[v] = n
        edges.append([p, n])
        edges.append([p, B])
        edges.append([n, B])

    def lit_vertex(lit):
        v = abs(lit)
        return pos[v] if lit > 0 else neg[v]

    def new_vertex():
        nonlocal next_id
        v = next_id
        next_id += 1
        return v

    def not_gate(x):
        # y is adjacent to B and x, so y is the opposite of x among T/F.
        y = new_vertex()
        edges.append([y, B])
        edges.append([y, x])
        return y

    def nand_gate(p, q):
        # Triangle u, v, w.  u is adjacent to p and v is adjacent to q.
        u = new_vertex()
        v = new_vertex()
        w = new_vertex()
        edges.append([u, v])
        edges.append([v, w])
        edges.append([w, u])
        edges.append([u, p])
        edges.append([v, q])
        # Output n is adjacent to B and w.
        n = new_vertex()
        edges.append([n, B])
        edges.append([n, w])
        return n

    def or_gate(a, b):
        # a OR b = NAND(NOT a, NOT b)
        na = not_gate(a)
        nb = not_gate(b)
        return nand_gate(na, nb)

    for clause in clauses:
        l1, l2, l3 = clause
        a = lit_vertex(l1)
        b = lit_vertex(l2)
        c = lit_vertex(l3)
        n1 = or_gate(a, b)
        n2 = or_gate(n1, c)
        # Force the clause output to be true (T).
        edges.append([n2, F])

    # Deduplicate edges.  The construction does not create duplicates, but
    # this guarantees the exact target format.
    seen = set()
    unique_edges = []
    for u, v in edges:
        if u == v:
            continue
        key = (u, v) if u < v else (v, u)
        if key not in seen:
            seen.add(key)
            unique_edges.append([u, v])

    return {"n": next_id, "edges": unique_edges}
