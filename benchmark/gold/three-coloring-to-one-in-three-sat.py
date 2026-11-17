"""Gold reduction: 3-Coloring -> 1-in-3-SAT.         [difficulty: 6 of 6]

SOURCE  3-Coloring  {"n": n, "edges": [[u, v], ...]}
TARGET  1-in-3-SAT  {"num_vars": m, "clauses": [[a, b, c], ...]}
        3 different POSITIVE variables per clause; yes iff some assignment
        makes EXACTLY ONE variable in every clause true.

Construction
  1. One variable per (vertex, colour): x(v, c) for v in 0..n-1, c in 0..2.
  2. Each vertex gets exactly one colour, which is a 1-in-3 clause directly:
       [x(v, 0), x(v, 1), x(v, 2)]
  3. Adjacent vertices must not share colour c: "not both x(u, c) and
     x(w, c)". 1-in-3-SAT has no negations, so use a fresh SLACK variable
     s(e, c) for each edge e and colour c:
       [x(u, c), x(w, c), s(e, c)]
     Exactly one of the three is true, so at most one endpoint has colour c,
     and the slack absorbs the case where neither does.
  4. num_vars = 3 * n + 3 * |E|. Number the slacks after all the x variables.

Check both directions on paper
  * Given a proper colouring, how do you set every slack variable?
  * Given a satisfying assignment, why is the colouring proper?

Edge cases
  * n = 0: no variables, no clauses, yes.
  * Edges listed as [u, v] or [v, u] are the same edge; each needs one set of
    3 slack variables.

Broken versions to try
  * Reuse one slack variable per edge for all 3 colours.
  * Forget the per-vertex clauses (vertices may end up with no colour).

Check it:
  uv run python -m benchmark.verify --reduce benchmark/gold/three-coloring-to-one-in-three-sat.py --task three-coloring-to-one-in-three-sat
"""

def var(v, c):
    return 3 * v + c + 1

def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    clauses = [[var(v, 0), var(v, 1), var(v, 2)] for v in range(n)]

    for j, (u, w) in enumerate(edges):
        for c in range(3):
          slack = 3 * n + 3 * j + c + 1
          clauses.append([var(u, c), var(w, c), slack])

    return {"num_vars": 3*n + 3*len(edges), "clauses": clauses}