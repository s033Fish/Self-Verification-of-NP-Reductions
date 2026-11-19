"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Encoding
--------
For a graph with ``n`` vertices we introduce three boolean variables per
vertex, ``x[v][c]`` (``v`` in ``0..n-1``, ``c`` in ``0..2``), meaning
"vertex ``v`` receives colour ``c``".  One extra fresh variable ``z`` is
used purely as a padding literal.

Constraints (all translated to clauses with exactly three literals on
three distinct variables):

* Every vertex gets at least one colour:
      (x[v][0] or x[v][1] or x[v][2])
* Every vertex gets at most one colour, for each pair c < d:
      (not x[v][c] or not x[v][d])
  A two-literal clause is padded with the fresh variable ``z`` by adding
  BOTH (a or b or z) and (a or b or not z); together these force (a or b)
  for either value of ``z``.
* Every edge's endpoints differ, for each colour c:
      (not x[u][c] or not x[v][c])
  padded in the same way.

The formula is satisfiable iff the graph is 3-colourable, and it has
O(n + |E|) variables and clauses, so the reduction is polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Variables 1..3n encode x[v][c]; variable 3n+1 is the padding variable.
    num_vars = 3 * n + 1
    z = num_vars

    def var(v, c):
        # v in 0..n-1, c in 0..2  ->  a variable in 1..3n
        return 3 * v + c + 1

    clauses = []

    # At least one colour per vertex.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    def add_two(a, b):
        # Force the two-literal clause (a or b) using the fresh variable z.
        clauses.append([a, b, z])
        clauses.append([a, b, -z])

    # At most one colour per vertex.
    for v in range(n):
        for c in range(3):
            for d in range(c + 1, 3):
                add_two(-var(v, c), -var(v, d))

    # Adjacent vertices must not share a colour.
    for u, w in edges:
        for c in range(3):
            add_two(-var(u, c), -var(w, c))

    return {"num_vars": num_vars, "clauses": clauses}
