"""Gold reduction: 3-SAT -> 3-Coloring.              [difficulty: 8 of 8]

SOURCE  3-SAT       {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
TARGET  3-Coloring  {"n": n, "edges": [[u, v], ...]}
        yes iff each vertex can get one of 3 colours, adjacent ones differing.

Construction (the textbook one, e.g. Sipser / Kleinberg-Tardos)
  1. Palette: a triangle of three vertices T, F, B (true, false, base). In
     any 3-colouring they get three different colours; call those colours
     "true", "false" and "base".
  2. Variables: for each variable v, vertices pos(v) and neg(v) forming a
     triangle with B. So each of them is coloured true or false, and they
     get opposite colours: a truth assignment.
  3. OR gadget OR(a, b) -> o, built from three new vertices x, y, o:
       edges a-x, b-y, x-y, x-o, y-o
     Claim: o can be coloured "true" iff a or b is coloured "true", and if
     a and b are both "false", then o must be "false". Check this claim by
     hand with a small table; it is the heart of the reduction.
  4. Clauses: for clause (l1 or l2 or l3), chain two gadgets,
       o1 = OR(l1, l2),  o2 = OR(o1, l3),
     where a literal l means pos(v) if l = +v and neg(v) if l = -v.
     Then join o2 to F and to B, which forces o2 to be "true".
  Size: 3 + 2m + 6c vertices. Keep a counter for the next free vertex.
"""


def reduce(instance):
    m = instance["num_vars"]
    T, F, B = 0, 1, 2

    def pos(v):
        return 3 + 2 * (v - 1)

    def neg(v):
        return 4 + 2 * (v - 1)

    def literal(l):
        return pos(l) if l > 0 else neg(-l)

    edges = [[T, F], [F, B], [T, B]]
    for v in range(1, m + 1):
        edges += [[pos(v), neg(v)], [pos(v), B], [neg(v), B]]

    n = 3 + 2 * m

    def or_gadget(a, b):
        nonlocal n
        x, y, out = n, n + 1, n + 2
        n += 3
        edges.extend([[a, x], [b, y], [x, y], [x, out], [y, out]])
        return out

    for l1, l2, l3 in instance["clauses"]:
        out = or_gadget(or_gadget(literal(l1), literal(l2)), literal(l3))
        edges += [[out, F], [out, B]]
    return {"n": n, "edges": edges}