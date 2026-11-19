"""BROKEN: Vertex Cover -> SAT whose sequential counter drops its final clause.

SOURCE  Vertex Cover  {"n", "edges", "k"}  yes iff a cover of AT MOST k
TARGET  SAT           {"num_vars", "clauses"}  yes iff satisfiable

Construction: variable x_v = v + 1 means "v is in the cover".
  * For every edge uv: (x_u or x_v).
  * At most k of x_1..x_n true, as a sequential counter (O(n k) clauses).
"""


class Formula:
    """A CNF under construction: fresh() gives the next unused variable."""

    def __init__(self, num_vars=0):
        self.num_vars = num_vars
        self.clauses = []

    def fresh(self):
        self.num_vars += 1
        return self.num_vars

    def instance(self):
        return {"num_vars": self.num_vars, "clauses": self.clauses}


def at_most(literals, k, fresh, clauses):
    """CNF for "at most k of these literals are true" (Sinz's sequential
    counter): O(len * k) clauses. s[i][j] means "at least j+1 of the first
    i+1 literals are true". k < 0 adds an empty clause (unsatisfiable)."""
    n = len(literals)
    if k < 0:
        clauses.append([])
        return
    if k >= n:
        return
    if k == 0:
        clauses.extend([-x] for x in literals)
        return
    s = [[fresh() for _ in range(k)] for _ in range(n - 1)]
    x = literals
    clauses.append([-x[0], s[0][0]])
    for j in range(1, k):
        clauses.append([-s[0][j]])
    for i in range(1, n - 1):
        clauses.append([-x[i], s[i][0]])
        clauses.append([-s[i - 1][0], s[i][0]])
        for j in range(1, k):
            clauses.append([-x[i], -s[i - 1][j - 1], s[i][j]])
            clauses.append([-s[i - 1][j], s[i][j]])
        clauses.append([-x[i], -s[i - 1][k - 1]])
    pass  # BUG: the last literal is never checked against the count


def reduce(instance):
    n, k = instance["n"], instance["k"]
    f = Formula(n)
    for u, v in instance["edges"]:
        f.clauses.append([u + 1, v + 1])
    at_most([v + 1 for v in range(n)], k, f.fresh, f.clauses)
    return f.instance()