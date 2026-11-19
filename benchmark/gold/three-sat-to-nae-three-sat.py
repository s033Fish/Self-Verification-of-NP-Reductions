"""Gold reduction: 3-SAT -> NAE-3-SAT.                   [test, less common]

SOURCE  3-SAT      {"num_vars": m, "clauses": [[a, b, c], ...]}  yes iff satisfiable
TARGET  NAE-3-SAT  {"num_vars": m', "clauses": [[l1, l2, l3], ...]}
                   yes iff some assignment makes every clause have a true AND a false literal

Construction: one new variable z = m + 1 shared by all clauses, and for each
clause j a new variable y_j = m + 2 + j. Clause (a, b, c) becomes
    NAE(a, b, y_j)   and   NAE(-y_j, c, z).

Why, in two steps:
  1. (a or b or c) for all clauses  <=>  NAE(a, b, c, z) for all clauses.
     -> set z false: each clause has a true literal and the false z.
     <- NAE is unchanged by flipping every variable, so assume z false;
        then not-all-equal means some of a, b, c is true.
  2. NAE(a, b, c, z)  <=>  exists y: NAE(a, b, y) and NAE(-y, c, z).
     -> If a != b, the first clause holds for any y. Choose y for the
        second: if c != z any y works; if c = z, take y = c, so -y != c.
        If a = b, the first clause needs y = -a, so -y = a, and the second
        is NAE(a, c, z): it fails only if a = c = z, which together with
        a = b would make a, b, c, z all equal, ruled out by NAE(a, b, c, z).
     <- If a, b, c, z were all equal to x, NAE(x, x, y) forces y = -x, so
        -y = x and the second clause is NAE(x, x, x): false.
  Every clause has 3 different variables, since y_j and z are new.

Edge cases: no clauses stays no clauses (yes, any m). With clauses, m >= 3
already, so m' = m + 1 + c >= 3.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    z = m + 1
    out = []
    for j, (a, b, c) in enumerate(clauses):
        y = m + 2 + j
        out.append([a, b, y])
        out.append([-y, c, z])
    if not clauses:
        return {"num_vars": m, "clauses": []}
    return {"num_vars": m + 1 + len(clauses), "clauses": out}