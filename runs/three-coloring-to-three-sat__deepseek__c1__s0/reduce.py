"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Source instance: {"n": n, "edges": [[u, v], ...]}
Target instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Encoding
--------
For every vertex v in 0..n-1 and colour c in {0, 1, 2} introduce a boolean
variable x[v, c] meaning "vertex v gets colour c".  Variables are numbered
1..3n as

    x[v, c] = 3*v + c + 1.

The formula contains:

* for each vertex v:  (x[v,0] or x[v,1] or x[v,2])          -- at least one colour
* for each vertex v and each pair c < c':
      (not x[v,c] or not x[v,c'])                          -- at most one colour
* for each edge {u, w} and each colour c:
      (not x[u,c] or not x[w,c])                           -- endpoints differ

The "at most one colour" and "edge" clauses have only two literals, while
3-SAT requires exactly three literals on three distinct variables.  Each
such clause (a or b) is replaced by the pair

    (a or b or d), (a or b or not d)

where d is a single fresh dummy variable shared by all padded clauses.
For any truth values of a and b the pair is satisfied exactly when
(a or b) is satisfied: if a or b is true, d may be chosen freely; if both
are false then d would have to be both true and false.  The dummy occurs
nowhere else, so the padding preserves satisfiability exactly.

The construction uses O(n^2 + |E|) clauses and runs in polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    def var(v, c):
        return 3 * v + c + 1

    clauses = []

    # Each vertex has at least one colour.
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Each vertex has at most one colour.
    for v in range(n):
        for c in range(3):
            for d in range(c + 1, 3):
                clauses.append([-var(v, c), -var(v, d)])

    # Adjacent vertices must have different colours.
    for u, w in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(w, c)])

    num_vars = 3 * n

    # Pad every 2-literal clause to 3 literals with one shared dummy variable.
    if any(len(clause) == 2 for clause in clauses):
        num_vars += 1
        dummy = num_vars
        padded = []
        for clause in clauses:
            if len(clause) == 2:
                a, b = clause
                padded.append([a, b, dummy])
                padded.append([a, b, -dummy])
            else:
                padded.append(clause)
        clauses = padded

    return {"num_vars": num_vars, "clauses": clauses}
