"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
For a graph on n >= 3 vertices we introduce n*n boolean variables

    x[v][i]   (1-indexed as v*n + i + 1)

with the intended meaning "vertex v is the i-th vertex of the cycle"
(positions are taken modulo n).

The CNF contains:

1. For every position i, the clause  (x[0][i] or ... or x[n-1][i]):
   every position is occupied by at least one vertex.

2. For every vertex v and every pair of distinct positions i < j, the
   clause (~x[v][i] or ~x[v][j]): a vertex is used at most once.

3. For every position i and every pair of distinct vertices u < v, the
   clause (~x[u][i] or ~x[v][i]): a position holds at most one vertex.

   Clauses 1 and 3 together force exactly one vertex per position, and
   clause 2 then forces those n vertices to be pairwise distinct, i.e. a
   permutation of the vertices.

4. For every position i (with next position j = (i+1) mod n) and every
   ordered pair of distinct, non-adjacent vertices (u, v), the clause
   (~x[u][i] or ~x[v][j]): consecutive vertices of the cycle must be
   joined by an edge of the graph.

A satisfying assignment is exactly a Hamiltonian cycle and vice versa.

For n <= 2 the answer is always "no" (a simple graph needs at least three
vertices for a cycle), so we emit the trivially unsatisfiable formula
with no variables and the empty clause.

The formula has n^2 variables and O(n^3) clauses, so the reduction runs
in polynomial time.
"""

from itertools import combinations


def reduce(instance):
    """Reduce a Hamiltonian Cycle instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Graphs with fewer than 3 vertices can never contain a cycle.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    edge_set = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    def var(vertex, position):
        # Variables are 1..n*n.
        return vertex * n + position + 1

    clauses = []

    # 1. Every position has at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. Every vertex occurs at most once.
    for v in range(n):
        for i, j in combinations(range(n), 2):
            clauses.append([-var(v, i), -var(v, j)])

    # 3. Every position contains at most one vertex.
    for i in range(n):
        for u, v in combinations(range(n), 2):
            clauses.append([-var(u, i), -var(v, i)])

    # 4. Consecutive positions must be connected by an edge.
    for i in range(n):
        nxt = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                a, b = (u, v) if u < v else (v, u)
                if (a, b) not in edge_set:
                    clauses.append([-var(u, i), -var(v, nxt)])

    return {"num_vars": n * n, "clauses": clauses}
