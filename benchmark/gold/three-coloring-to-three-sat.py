"""Gold reduction: 3-Coloring -> 3-SAT.                  [test, less common]

SOURCE  3-Coloring  {"n", "edges"}  yes iff 3-colourable
TARGET  3-SAT       {"num_vars", "clauses"}  3 different variables per clause

Construction: variable c(v, col) = 3v + col + 1 means "v may take colour col".
  * Every vertex gets some colour: (c(v,0), c(v,1), c(v,2)).
  * For every edge uv and colour col, not both: (-c(u,col) or -c(v,col)).
    3-SAT needs 3 literals, so pad with a fresh variable y:
        (-c(u,col), -c(v,col), y)  and  (-c(u,col), -c(v,col), -y)
    Both hold iff (-c(u,col) or -c(v,col)) holds.

"""


def reduce(instance):
    n = instance["n"]

    def c(v, col):
        return 3 * v + col + 1

    clauses = [[c(v, 0), c(v, 1), c(v, 2)] for v in range(n)]
    next_var = 3 * n
    for u, v in instance["edges"]:
        for col in range(3):
            next_var += 1
            clauses.append([-c(u, col), -c(v, col), next_var])
            clauses.append([-c(u, col), -c(v, col), -next_var])
    return {"num_vars": next_var, "clauses": clauses}