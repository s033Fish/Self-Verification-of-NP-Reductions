"""Polynomial-time reduction from 3-Coloring to 3-SAT.

For a graph with vertices 0..n-1 introduce variables

    x_{v,c} = 3*v + c + 1        (1 <= x_{v,c} <= 3n)

for c in {0, 1, 2}, meaning "vertex v has colour c".

* For every vertex v add the 3-clause
      (x_{v,0} or x_{v,1} or x_{v,2})
  forcing at least one colour.

* For every edge {u, v} and every colour c add the 2-clause
      (not x_{u,c} or not x_{v,c})
  forbidding both endpoints from receiving colour c.  A 2-clause (a or b)
  is replaced by the two 3-clauses
      (a or b or p) and (a or b or not p)
  where p is a fresh variable; together these are logically equivalent to
  (a or b), and each has three literals on three distinct variables.

A satisfying assignment yields a proper 3-colouring by choosing, for each
vertex, any colour whose variable is true.  Conversely a proper colouring
extends to a satisfying assignment (set the padding variables freely).
The construction uses O(n + |E|) variables and clauses.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    num_vars = 3 * n

    def colour_var(v, c):
        # Variables are 1-indexed.
        return 3 * v + c + 1

    clauses = []

    # At least one colour per vertex.
    for v in range(n):
        clauses.append([colour_var(v, 0), colour_var(v, 1), colour_var(v, 2)])

    def add_binary(a, b):
        """Add the 2-clause (a or b), encoded with two 3-clauses."""
        nonlocal num_vars
        num_vars += 1
        p = num_vars
        clauses.append([a, b, p])
        clauses.append([a, b, -p])

    # Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            add_binary(-colour_var(u, c), -colour_var(v, c))

    return {"num_vars": num_vars, "clauses": clauses}
