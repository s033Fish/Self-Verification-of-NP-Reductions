"""Polynomial-time reduction from 3-Coloring to 3-SAT.

Source instance:
    {"n": n, "edges": [[u, v], ...]}

Target instance:
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Encoding:
    For each vertex v and colour c in {0,1,2}, variable X(v,c) means
    "vertex v has colour c".  We add clauses forcing exactly one colour
    per vertex and forbidding equal colours on every edge.

    Since 3-SAT requires exactly three literals per clause, every
    2-literal constraint (not both x and y) is represented by two
    3-literal clauses using one fresh auxiliary variable z:
        (-x or -y or z) and (-x or -y or -z)
    If x and y are both true these force z and -z; otherwise they are
    satisfied for either value of z.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # A graph with no vertices is trivially 3-colourable; the empty
    # 3-SAT formula is satisfiable.
    if n <= 0:
        return {"num_vars": 0, "clauses": []}

    # Variables 1..3n encode the colour of each vertex.
    num_vars = 3 * n
    clauses = []

    def x(v, c):
        # 1-based variable for "vertex v has colour c".
        return 3 * v + c + 1

    # Exactly one colour per vertex.
    for v in range(n):
        # At least one colour.
        clauses.append([x(v, 0), x(v, 1), x(v, 2)])

        # At most one colour: for each pair of colours, add two clauses
        # with a fresh auxiliary variable.
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                num_vars += 1
                z = num_vars
                clauses.append([-x(v, c1), -x(v, c2), z])
                clauses.append([-x(v, c1), -x(v, c2), -z])

    # Adjacent vertices must have different colours.
    for u, v in edges:
        for c in range(3):
            num_vars += 1
            z = num_vars
            clauses.append([-x(u, c), -x(v, c), z])
            clauses.append([-x(u, c), -x(v, c), -z])

    return {"num_vars": num_vars, "clauses": clauses}
