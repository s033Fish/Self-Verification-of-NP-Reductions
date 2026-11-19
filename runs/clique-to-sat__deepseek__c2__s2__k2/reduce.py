"""Polynomial-time reduction from Clique to SAT.

Clique instance: {"n": n, "edges": [[u, v], ...], "k": k}
SAT instance:    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For each clique position i in 0..k-1 and each vertex v in 0..n-1 introduce a
Boolean variable x_{i,v} (numbered i*n + v + 1).  Intuitively x_{i,v} is true
when vertex v is the i-th vertex of the chosen clique.

Clauses:
  * For every position i, the clause [x_{i,0}, ..., x_{i,n-1}] forces at least
    one vertex to be chosen for that position.
  * For every position i and every pair u < v, the clause
    [-x_{i,u}, -x_{i,v}] forces at most one vertex to be chosen for position i.
  * For every pair of positions i < j and every ordered pair of distinct
    vertices (u, v) that is NOT an edge, the clause [-x_{i,u}, -x_{j,v}]
    forbids choosing non-adjacent vertices at two different positions.

A satisfying assignment therefore selects exactly one vertex per position, and
all selected vertices are pairwise adjacent: a clique of size k.  Conversely a
clique of size >= k yields a satisfying assignment by choosing k of its
vertices.  Hence the answer is preserved.

Edge cases (handled without building the general formula):
  * k <= 0: Clique is always yes; return the empty CNF, which is satisfiable.
  * k > n:  Clique is always no; return a CNF containing the empty clause,
            which is unsatisfiable.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Clique with k <= 0 is always yes: the empty formula is satisfiable.
    if k <= 0:
        return {"num_vars": 0, "clauses": []}

    # A clique cannot have more than n vertices: emit an unsatisfiable formula.
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Now 1 <= k <= n.  Number x_{i,v} as i*n + v + 1 for i in 0..k-1,
    # v in 0..n-1, so there are k*n variables.
    def var(i, v):
        return i * n + v + 1

    # Undirected edge lookup.
    edge_set = set()
    for u, v in edges:
        edge_set.add(frozenset((u, v)))

    clauses = []

    # At least one vertex per position.
    for i in range(k):
        clauses.append([var(i, v) for v in range(n)])

    # At most one vertex per position.
    for i in range(k):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Distinct positions must hold adjacent vertices.
    for i in range(k):
        for j in range(i + 1, k):
            for u in range(n):
                for v in range(n):
                    if u == v:
                        continue
                    if frozenset((u, v)) not in edge_set:
                        clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": k * n, "clauses": clauses}
