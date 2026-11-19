"""Polynomial-time reduction from 3-SAT to Dominating Set.

Source instance (3-SAT):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Literals are +v (v true) or -v (v false), v in 1..m.

Target instance (Dominating Set):
    {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
* Variable gadget: for each variable v (1..m) add two vertices
      T_v = 2*(v-1)        (represents v true)
      F_v = 2*(v-1) + 1    (represents v false)
  joined by the edge [T_v, F_v].
* Clause gadget: for each clause add one new vertex c, and connect c to
  the literal vertex of each of its three literals (T_v for +v, F_v for -v).
* Set k = m.

Correctness
-----------
(<=) Given a satisfying assignment, choose for every variable the vertex of
its gadget matching the assigned value.  This is m vertices and dominates
every variable gadget.  Each clause has a true literal, so its clause vertex
is adjacent to the chosen literal vertex and is dominated.  Thus a
dominating set of size m exists.

(=>) Suppose D is a dominating set with |D| <= m.  If some variable gadget
v had neither T_v nor F_v in D, then both would have to be dominated by
clause vertices; since no clause contains both v and -v, no single clause
vertex is adjacent to both T_v and F_v, so this needs at least two clause
vertices of D.  Counting over all gadgets: if a gadgets have no chosen
vertex and b have at least one (a + b = m), then |D| >= 2a + b = m + a.
Since |D| <= m we get a = 0, so D contains at least one vertex of every
variable gadget.  Hence |D| >= m and with |D| <= m it contains exactly one
vertex per gadget and no clause vertices.  Every clause vertex must be
adjacent to a chosen variable vertex, i.e. one of its literals is true.
Hence the assignment defined by the chosen vertices satisfies all clauses.

The construction uses O(m + |clauses|) vertices and edges, so it runs in
polynomial time.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    edges = []
    # Variable gadgets: T_v = 2*(v-1), F_v = 2*(v-1)+1.
    for v in range(1, m + 1):
        edges.append([2 * (v - 1), 2 * (v - 1) + 1])

    n = 2 * m
    # Clause gadgets.
    for clause in clauses:
        c = n
        n += 1
        for lit in clause:
            var = abs(lit) - 1
            if lit > 0:
                # +v -> T_v
                edges.append([c, 2 * var])
            else:
                # -v -> F_v
                edges.append([c, 2 * var + 1])

    return {"n": n, "edges": edges, "k": m}
