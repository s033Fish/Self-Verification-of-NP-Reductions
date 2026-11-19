"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
For a graph with n >= 3 vertices we introduce one boolean variable

    x(v, i)   meaning "vertex v is visited at position i of the cycle"

for every v in 0..n-1 and i in 0..n-1, numbered 1..n*n.

The clauses enforce:

  * every position holds at least one vertex   (at-least-one per position)
  * every position holds at most one vertex    (at-most-one per position)
  * every vertex occupies at least one position (at-least-one per vertex)
  * every vertex occupies at most one position  (at-most-one per vertex)
  * consecutive positions (cyclically) are joined by an edge: for every
    ordered pair (u, v) that is NOT an edge and every position i, we add
    (~x(u, i) OR ~x(v, (i+1) mod n)).

A satisfying assignment is exactly a cyclic ordering of all vertices in
which every consecutive pair is an edge, i.e. a Hamiltonian cycle.

Graphs with n <= 2 can never have a Hamiltonian cycle, so they are mapped
to the unsatisfiable formula containing the empty clause.

The formula has n*n variables and O(n^4) clauses, so the reduction runs in
polynomial time and does not call any solver.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: no simple cycle can visit every vertex exactly once.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    def var(v, i):
        return v * n + i + 1

    num_vars = n * n
    clauses = []

    # Exactly one vertex per position.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # Exactly one position per vertex.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # Adjacency of consecutive positions (cyclically).
    adjacent = set()
    for u, v in edges:
        adjacent.add(frozenset((u, v)))

    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if frozenset((u, v)) in adjacent:
                continue
            for i in range(n):
                clauses.append([-var(u, i), -var(v, (i + 1) % n)])

    return {"num_vars": num_vars, "clauses": clauses}
