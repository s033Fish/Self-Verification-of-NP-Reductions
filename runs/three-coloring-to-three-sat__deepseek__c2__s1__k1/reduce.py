"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]} with vertices 0..n-1.
Target instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}.

Construction
------------
For every vertex v in 0..n-1 and colour c in {0, 1, 2} introduce a Boolean
variable x_{v,c} meaning "vertex v receives colour c".  Number the variables
1..3n as 3*v + c + 1.

* For each vertex v add the clause (x_{v,0} v x_{v,1} v x_{v,2}): every
  vertex gets at least one colour.  This already has 3 literals on 3 distinct
  variables.

* For each edge {u, v} and each colour c the 2-literal clause
  (~x_{u,c} v ~x_{v,c}) forbids both endpoints from sharing colour c.  The
  target format only allows 3-literal clauses, so replace it by a fresh
  variable z and the two clauses
        (~x_{u,c} v ~x_{v,c} v  z)
        (~x_{u,c} v ~x_{v,c} v ~z)
  which together are satisfiable exactly when ~x_{u,c} v ~x_{v,c} is: if the
  first two literals are both false the two clauses force z and ~z, and
  otherwise both clauses are already satisfied regardless of z.  The three
  literals involve the distinct variables x_{u,c}, x_{v,c}, z.

Correctness
-----------
A proper 3-colouring yields a satisfying assignment by setting x_{v,c} true
iff v has colour c, and choosing z arbitrarily.  Conversely, any satisfying
assignment has, for every vertex v, some true x_{v,c}; for every edge {u,v}
and colour c it cannot be that x_{u,c} and x_{v,c} are both true (otherwise
the two z-clauses would require z and ~z).  Picking any true colour of each
vertex therefore gives a proper 3-colouring.

Size: 3n + 3|E| variables and n + 6|E| clauses, so the reduction is
polynomial time and output size.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to a 3-SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n
    clauses = []

    def color_var(vertex, color):
        # Variables are 1-based: vertex 0..n-1, colour 0..2.
        return 3 * vertex + color + 1

    # Each vertex must receive at least one of the three colours.
    for v in range(n):
        clauses.append([color_var(v, 0), color_var(v, 1), color_var(v, 2)])

    # Adjacent vertices may not share a colour.  Each forbidden pair is a
    # 2-literal clause, expanded into two 3-literal clauses with a fresh
    # variable so that the target's exactly-3-distinct-variables rule holds.
    for u, v in edges:
        for c in range(3):
            num_vars += 1
            z = num_vars
            a = -color_var(u, c)
            b = -color_var(v, c)
            clauses.append([a, b, z])
            clauses.append([a, b, -z])

    return {"num_vars": num_vars, "clauses": clauses}
