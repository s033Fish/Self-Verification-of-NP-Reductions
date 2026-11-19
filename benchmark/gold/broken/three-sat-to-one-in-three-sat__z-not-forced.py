"""BROKEN: 3-SAT -> 1-in-3-SAT without the gadget that forces Z false.

SOURCE  3-SAT       {"num_vars": m, "clauses": [[l1, l2, l3], ...]}  yes iff satisfiable
TARGET  1-in-3-SAT  {"num_vars", "clauses": [[a, b, c], ...]}  POSITIVE variables only;
                    yes iff some assignment makes EXACTLY ONE variable per clause true

Write R(a, b, c) for a 1-in-3 clause. The target has no negations, so:
  1. A variable Z forced false, with helpers A, B, Y, W:
       R(A, B, Z), R(A, B, Y), R(Z, Y, W)
     If Z were true, A = B = false, so Y is true, and R(Z, Y, W) has two
     trues. With Z false, take A true, Y false, W true.
  2. For each source variable v, two variables P_v ("v true") and N_v
     ("v false") with R(P_v, N_v, Z): since Z is false, exactly one holds.
     So every literal has a positive variable, and its negation is the
     partner: lit(+v) = P_v, lit(-v) = N_v, and ~lit swaps them.
  3. For each clause (x, y, z), four fresh a, b, c, d (Schaefer's gadget):
       R(~x, a, b), R(b, y, c), R(c, d, ~z)
     These can be satisfied iff x or y or z is true (checked over all 8
     cases of x, y, z and 16 of a, b, c, d).
"""


def reduce(instance):
    m, clauses = instance["num_vars"], instance["clauses"]
    if not clauses:
        return {"num_vars": 0, "clauses": []}
    count = 0

    def fresh():
        nonlocal count
        count += 1
        return count

    out = []
    z, a, b, y, w = (fresh() for _ in range(5))
    # BUG: Z is never forced false, so Z true lets every P_v, N_v be false
    positive = {v: fresh() for v in range(1, m + 1)}
    negative = {v: fresh() for v in range(1, m + 1)}
    for v in range(1, m + 1):
        out.append([positive[v], negative[v], z])

    def lit(l):
        return positive[l] if l > 0 else negative[-l]

    for x, yy, zz in clauses:
        g1, g2, g3, g4 = (fresh() for _ in range(4))
        out += [[lit(-x), g1, g2], [g2, lit(yy), g3], [g3, g4, lit(-zz)]]
    return {"num_vars": count, "clauses": out}