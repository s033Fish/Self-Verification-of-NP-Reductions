"""Polynomial-time reduction from NAE-3-SAT to 3-Coloring.

Input  (NAE-3-SAT): {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Output (3-Coloring): {"n": n, "edges": [[u, v], ...]}

Construction
------------
Three "palette" vertices T=0, F=1, B=2 form a triangle, so every
3-colouring gives them the three distinct colours.  We read T as true,
F as false, and B as a neutral colour that no literal vertex may use.

For each variable v, add vertices pos(v) and neg(v).  Both are joined to
B and to each other.  Since they are adjacent to each other and both
adjacent to B, they must receive the two colours other than B: one is T
and the other F.  This encodes a truth assignment (pos true iff T).

For each clause (l1, l2, l3), add a fresh triangle a, b, c and join the
vertex representing l1 to a, l2 to b and l3 to c.  The triangle a, b, c
uses all three colours.  If all three literals had the same colour, then
a, b, c would each have to avoid that colour and could use only the
other two, impossible for a triangle.  Hence all-equal is forbidden.
If the literals are not all equal, the gadget can always be coloured
(the triangle takes the colour missing from the literals), so the clause
is satisfied.

Therefore the graph is 3-colourable iff the formula is a yes-instance.
The construction uses O(m + number_of_clauses) vertices and edges, so it
runs in polynomial time and never calls a solver.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Palette triangle: 0 = true, 1 = false, 2 = neutral/base.
    T, F, B = 0, 1, 2
    edges = [[T, F], [F, B], [T, B]]

    # One pair of vertices per variable.
    pos = {}
    neg = {}
    next_vertex = 3
    for v in range(1, m + 1):
        p = next_vertex
        n = next_vertex + 1
        next_vertex += 2
        pos[v] = p
        neg[v] = n
        edges.append([p, n])   # pos(v) and neg(v) get different colours
        edges.append([p, B])   # neither may use the neutral colour
        edges.append([n, B])

    # One 6-edge gadget per clause.
    for clause in clauses:
        a = next_vertex
        b = next_vertex + 1
        c = next_vertex + 2
        next_vertex += 3

        # Triangle a, b, c (forces three distinct colours).
        edges.append([a, b])
        edges.append([b, c])
        edges.append([a, c])

        # Attach the three literal vertices.
        for literal, gadget_vertex in zip(clause, (a, b, c)):
            if literal > 0:
                lit_vertex = pos[literal]
            else:
                lit_vertex = neg[-literal]
            edges.append([lit_vertex, gadget_vertex])

    return {"n": next_vertex, "edges": edges}
