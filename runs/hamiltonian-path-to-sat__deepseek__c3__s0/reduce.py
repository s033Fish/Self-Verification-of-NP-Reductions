"""Polynomial-time reduction from Hamiltonian Path (undirected, any
endpoints) to SAT (CNF satisfiability).

Idea
----
A Hamiltonian path is an ordering of all n vertices such that consecutive
vertices are joined by an edge.  Introduce boolean variables

    x[v][i]  ==  "vertex v occupies position i of the path"   (0 <= i < n)

and encode the existence of such an ordering with clauses:

  * Every position holds at least one vertex:
        (x[0][i] or x[1][i] or ... or x[n-1][i])        for each i
  * No vertex is used twice:
        (-x[v][i] or -x[v][j])                          for each v, i < j
  * No position holds two vertices:
        (-x[u][i] or -x[v][i])                          for each i, u < v
  * Consecutive positions must be adjacent:
        (-x[u][i] or -x[v][i+1])                        for each i < n-1
                                                        and each non-edge {u,v}

The first three families force a bijection between vertices and positions
(n positions each get exactly one vertex, and no vertex repeats).  The
last family then forces consecutive vertices of that ordering to be
adjacent, i.e. a Hamiltonian path.  Conversely any Hamiltonian path
yields a satisfying assignment by setting x[v][i] true iff v is the i-th
vertex of the path.

Edge cases
----------
n = 0: no path exists, so emit the unsatisfiable formula (num_vars=0,
       clauses=[[]]).
n = 1: the single position clause (x[0][0]) is satisfiable -> yes.
n = 2: the adjacency clauses reduce to exactly the requirement that the
       edge {0,1} be present.

The encoding uses n^2 variables and O(n^3) clauses, so it is polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    if n == 0:
        # No Hamiltonian path; the empty clause is unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    def var(v, i):
        # Variables are numbered 1..n*n.
        return v * n + i + 1

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    clauses = []

    # Every position holds at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # No vertex is used twice.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # No position holds two vertices.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # Consecutive positions must be adjacent.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and (u, v) not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}
