"""Polynomial-time reduction from 3-SAT to 3-Coloring.

Colours: 0 = True, 1 = False, 2 = Base.
A base triangle (T,F,B) fixes the meaning of the colours.  For each variable
v we add two vertices v and ~v, both joined to Base and to each other, so one
gets colour T and the other colour F.

For each clause (l1,l2,l3) we add a triangle c1,c2,c3 and connect c_i to the
node of literal l_i.  If all three literals are False, each c_i must avoid
colour F and the triangle cannot be coloured with 3 colours.  If some literal
is True, say l1, set c1=False and colour c2,c3 with the two remaining colours
(the neighbours l2,l3 are False, so they only forbid colour F, which is fine).
Hence the graph is 3-colourable iff the formula is satisfiable.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    T, F, B = 0, 1, 2
    edges = [[T, F], [F, B], [T, B]]

    lit_node = {}
    nxt = 3
    for v in range(1, num_vars + 1):
        pos = nxt
        neg = nxt + 1
        nxt += 2
        lit_node[v] = pos
        lit_node[-v] = neg
        edges.append([pos, B])
        edges.append([neg, B])
        edges.append([pos, neg])

    for clause in clauses:
        c = [nxt, nxt + 1, nxt + 2]
        nxt += 3
        edges.append([c[0], c[1]])
        edges.append([c[1], c[2]])
        edges.append([c[0], c[2]])
        for i in range(3):
            edges.append([c[i], lit_node[clause[i]]])

    return {"n": nxt, "edges": edges}
