"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Source instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance: {"n": n, "edges": [[u, v], ...]}

Construction
------------
* A base triangle on vertices 0, 1, 2 guarantees the three colours are all
  distinct.  Vertex 2 is used as the "base" colour.
* For every variable v in 1..m we add two vertices pos_v and neg_v, joined by
  an edge and each joined to the base vertex 2.  Hence pos_v and neg_v must
  receive the two colours different from the base colour, and they differ from
  each other: they encode the truth value of v (one is "true", the other
  "false").
* For every clause (l1, l2, l3) we add a fresh triangle p, q, r and connect
  p, q, r to the vertices of l1, l2, l3 respectively.

The clause gadget is 3-colourable exactly when the three literal vertices are
not all the same colour (i.e. the clause is not all-equal): if all three share
a colour, then p, q, r must each avoid that colour and thus use only two
colours, impossible for a triangle; if the literals are not all equal, a proper
colouring of p, q, r exists (a perfect matching argument on the two used
literal colours).

Therefore the graph is 3-colourable iff the NAE-3-SAT instance is satisfiable.
The construction uses O(m + k) vertices and edges, so it runs in polynomial
time.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Base triangle: vertices 0, 1, 2.
    edges.append([0, 1])
    edges.append([1, 2])
    edges.append([0, 2])

    BASE = 2

    # Variable gadgets.
    pos = {}
    neg = {}
    nxt = 3
    for v in range(1, m + 1):
        p = nxt
        q = nxt + 1
        nxt += 2
        pos[v] = p
        neg[v] = q
        edges.append([p, q])       # pos_v != neg_v
        edges.append([p, BASE])    # pos_v avoids base colour
        edges.append([q, BASE])    # neg_v avoids base colour

    def lit_vertex(lit):
        v = abs(lit)
        return pos[v] if lit > 0 else neg[v]

    # Clause gadgets.
    for clause in clauses:
        a = lit_vertex(clause[0])
        b = lit_vertex(clause[1])
        c = lit_vertex(clause[2])

        p = nxt
        q = nxt + 1
        r = nxt + 2
        nxt += 3

        # Triangle p, q, r.
        edges.append([p, q])
        edges.append([q, r])
        edges.append([p, r])

        # Attach the triangle to the three literals.
        edges.append([p, a])
        edges.append([q, b])
        edges.append([r, c])

    return {"n": nxt, "edges": edges}
