"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Source instance (NAE-3-SAT):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Literals are +v / -v for variables 1..m.

Target instance (3-Coloring):
    {"n": n, "edges": [[u, v], ...]}

Construction
------------
Use three colours 0, 1, 2.  Pick a "base" vertex B (colour 2 in any
canonical colouring).

* For every variable v in 1..m create two vertices pos[v] and neg[v].
  Add the edges (B, pos[v]), (B, neg[v]) and (pos[v], neg[v]).
  Since pos[v] and neg[v] are both adjacent to B and to each other, they
  must receive the two colours different from B's colour: exactly one of
  them is "true" and the other is "false".

* For every clause (l1, l2, l3) create three fresh vertices u, v, w
  forming a triangle (edges u-v, v-w, w-u) and connect the literal
  vertices to it as ports: port(l1)-u, port(l2)-v, port(l3)-w, where
  port(+x) = pos[x] and port(-x) = neg[x].

  A triangle must use all three colours.  If the three ports all had the
  same colour, then u, v, w would each have to avoid that colour and
  hence could only use two colours, impossible for a triangle.  If the
  ports are not all equal, a valid colouring of the triangle exists.
  Thus the clause gadget is 3-colourable iff the clause is not all equal.

The graph is 3-colourable iff the formula has a satisfying NAE
assignment.  The construction uses 1 + 2m + 3k vertices and
3m + 6k edges (k = number of clauses), so it is polynomial time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []

    # Base vertex.
    base = 0
    n = 1

    # One pair of literal vertices per variable.
    pos = {}
    neg = {}
    for v in range(1, num_vars + 1):
        p = n
        q = n + 1
        n += 2
        pos[v] = p
        neg[v] = q
        edges.append([base, p])
        edges.append([base, q])
        edges.append([p, q])

    def port(literal):
        v = abs(literal)
        return pos[v] if literal > 0 else neg[v]

    # One NAE clause gadget per clause.
    for clause in clauses:
        u = n
        v = n + 1
        w = n + 2
        n += 3
        edges.append([u, v])
        edges.append([v, w])
        edges.append([w, u])
        edges.append([port(clause[0]), u])
        edges.append([port(clause[1]), v])
        edges.append([port(clause[2]), w])

    return {"n": n, "edges": edges}
