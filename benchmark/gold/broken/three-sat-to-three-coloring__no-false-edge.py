"""Broken: joins the clause output to B but not to F.

Nothing then stops the output from being coloured "false", so every clause
gadget can be coloured even when all its literals are false: unsatisfiable
formulas become 3-colourable. Expect wrong_answer_no_to_yes.
"""


def reduce(instance):
    m = instance["num_vars"]
    T, F, B = 0, 1, 2
    pos = lambda v: 3 + 2 * (v - 1)
    neg = lambda v: 4 + 2 * (v - 1)
    literal = lambda l: pos(l) if l > 0 else neg(-l)
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
        edges.append([out, B])
    return {"n": n, "edges": edges}