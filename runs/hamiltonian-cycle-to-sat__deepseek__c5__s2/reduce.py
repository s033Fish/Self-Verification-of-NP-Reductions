"""Polynomial-time reduction from Hamiltonian Cycle to SAT.

Encoding
--------
For a graph with n >= 3 vertices we use n*n boolean variables

    x[v][i]  <->  "vertex v is the i-th vertex of the cycle"   (0 <= v,i < n)

Variable number for (v, i) is  v*n + i + 1  (variables are 1..n*n).

Clauses:

1. Each position holds at least one vertex:
       (x[0][i] or x[1][i] or ... or x[n-1][i])            for every i

2. Each position holds at most one vertex:
       (not x[u][i] or not x[v][i])                        for every i, u < v

3. Each vertex is used at most once:
       (not x[v][i] or not x[v][j])                        for every v, i < j

   Together 1-3 force a bijection between positions and vertices.

4. Consecutive positions are joined by a graph edge.  For every position i
   (with j = (i+1) mod n) and every ordered pair u != v that is *not* an
   edge of the graph:
       (not x[u][i] or not x[v][j])

   Because u == v is already impossible (constraint 3), constraint 4 says
   exactly that the vertices in consecutive positions form an edge.

A satisfying assignment therefore describes a cyclic ordering of all n
vertices in which every consecutive pair (including the wrap-around pair)
is an edge -- i.e. a Hamiltonian cycle.  Conversely any Hamiltonian cycle
yields a satisfying assignment.

Edge cases: n <= 2 can never have a Hamiltonian cycle, so we return the
unsatisfiable formula containing the empty clause.  The construction uses
O(n^2) variables and O(n^3) clauses, hence runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: no simple graph on <= 2 vertices has a cycle -> unsatisfiable.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v) if u < v else (v, u))

    def var(v: int, i: int) -> int:
        return v * n + i + 1

    num_vars = n * n
    clauses = []

    # 1. at least one vertex per position
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. at most one vertex per position
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 3. each vertex appears at most once
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 4. consecutive positions must be adjacent in the graph
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                key = (u, v) if u < v else (v, u)
                if key not in edge_set:
                    clauses.append([-var(u, i), -var(v, j)])

    return {"num_vars": num_vars, "clauses": clauses}
