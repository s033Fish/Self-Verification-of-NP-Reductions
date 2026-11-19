"""Polynomial-time reduction from 3-SAT to Independent Set.

Source (3-SAT): {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target (Independent Set): {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
For every clause create a triangle of three new vertices, one per literal,
with all three pairwise edges (so at most one literal of each clause can be
chosen).  Then, for every variable v, add an edge between every vertex
labelled +v and every vertex labelled -v (so the chosen literals must agree
on a single truth assignment).  Finally set k = number of clauses.

Correctness
-----------
* If the formula is satisfiable, pick a satisfying assignment and, in each
  clause, one true literal.  These one-per-clause vertices form an
  independent set: no two are in the same triangle, and no two are
  contradictory because the assignment makes the chosen literals true.
  Hence there is an independent set of size k.
* If the graph has an independent set of size k, it must contain exactly one
  vertex from each of the k triangles (triangles are cliques and there are k
  of them).  Assign each variable the truth value of the selected literal
  (variables with no selected literal are arbitrary).  The consistency edges
  guarantee no variable is forced both ways, so every clause has a true
  literal and the formula is satisfiable.

The construction uses O(len(clauses)) vertices and O(len(clauses)^2) edges,
so it runs in polynomial time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = 3 * len(clauses)
    edges = []

    # vertex lists per variable for each polarity
    positive = {}
    negative = {}

    for i, clause in enumerate(clauses):
        base = 3 * i
        a, b, c = base, base + 1, base + 2

        # triangle: all three pairs are edges
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])

        for vertex, literal in zip((a, b, c), clause):
            if literal > 0:
                positive.setdefault(literal, []).append(vertex)
            else:
                negative.setdefault(-literal, []).append(vertex)

    # consistency edges: +v cannot coexist with -v
    for var in set(positive) | set(negative):
        for u in positive.get(var, ()):
            for v in negative.get(var, ()):
                edges.append([u, v])

    return {"n": n, "edges": edges, "k": len(clauses)}
