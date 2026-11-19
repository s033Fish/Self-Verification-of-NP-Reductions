"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Source instance (NAE-3-SAT):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Literals are +v / -v for variables 1..m.

Target instance (3-Coloring):
    {"n": n, "edges": [[u, v], ...]}
    Vertices 0..n-1, undirected edges, no loops / duplicates.

Construction
------------
* A base triangle on vertices T=0, F=1, B=2.  A proper 3-colouring must
  give these three vertices the three different colours; we read vertex 0's
  colour as "true" and vertex 1's colour as "false".
* For every variable v in 1..m, two vertices pos_v and neg_v, both joined
  to B and to each other.  This forces {pos_v, neg_v} to be the two
  non-base colours in some order, i.e. pos_v is true iff neg_v is false.
* For every clause (l1, l2, l3), a fresh triangle p, q, r with p, q, r
  joined to the literal vertices of l1, l2, l3 respectively.

Correctness
-----------
(=>) Given a satisfying NAE assignment, colour T/F according to the
     assignment (pos_v true-colour iff v is true, neg_v the opposite) and
     B with the base colour.  Every clause has at least one true and one
     false literal, so its three literal vertices are not all equal; the
     fresh triangle can then always be coloured with three distinct
     colours avoiding the colours of its three attachments.
(<=) Any proper 3-colouring gives the base triangle three distinct
     colours.  Each variable pair is forced to the two non-base colours
     and opposite, defining a truth assignment.  If some clause had all
     three literals equal, its gadget triangle p, q, r would each be
     forbidden one colour and thus restricted to only two colours, so they
     could not be pairwise distinct -- a contradiction.  Hence every
     clause is not-all-equal.

The graph has 3 + 2m + 3k vertices and 3 + 3m + 6k edges, so the
reduction runs in linear (hence polynomial) time.
"""


def reduce(instance):
    """Return a 3-Coloring instance yes iff the NAE-3-SAT instance is yes."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Base triangle: 0 = true, 1 = false, 2 = base.
    T, F, B = 0, 1, 2
    edges = [[T, F], [F, B], [T, B]]

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
        edges.append([p, q])   # pos_v and neg_v differ
        edges.append([p, B])   # neither is the base colour
        edges.append([q, B])

    def literal_vertex(literal):
        v = abs(literal)
        return pos[v] if literal > 0 else neg[v]

    # Clause gadgets: a fresh triangle attached to the three literal vertices.
    for clause in clauses:
        p = nxt
        q = nxt + 1
        r = nxt + 2
        nxt += 3
        edges.append([p, q])
        edges.append([q, r])
        edges.append([p, r])
        edges.append([p, literal_vertex(clause[0])])
        edges.append([q, literal_vertex(clause[1])])
        edges.append([r, literal_vertex(clause[2])])

    return {"n": nxt, "edges": edges}
