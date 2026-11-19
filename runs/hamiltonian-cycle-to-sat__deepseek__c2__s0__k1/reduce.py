"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Idea
----
A Hamiltonian cycle visits every vertex exactly once and returns to its
start.  In an undirected graph we may rotate any such cycle so that vertex
0 sits at position 0.  Hence it suffices to look for an ordering

    p_0 = 0, p_1, ..., p_{n-1}

of all n vertices such that every consecutive pair (p_i, p_{i+1 mod n}) is
an edge of the graph.

Variables
---------
For i, v in 0..n-1 let x(i, v) be the boolean variable meaning
"vertex v is the i-th vertex of the cycle".  Variables are numbered
1..n*n via  x(i, v) = i*n + v + 1.

Clauses
-------
* Exactly one vertex per position:
    - (x(i,0) or ... or x(i,n-1))                       for every i
    - (-x(i,u) or -x(i,v)) for every i and u < v
* Every vertex at exactly one position:
    - (x(0,v) or ... or x(n-1,v))                       for every v
    - (-x(i,v) or -x(j,v)) for every v and i < j
* Vertex 0 starts the cycle: (x(0,0))
* Consecutive positions must be joined by an edge.  For every i, with
  j = (i+1) mod n, and every ordered pair (u, v) such that {u, v} is NOT
  an edge (u == v included), add (-x(i,u) or -x(j,v)).

A satisfying assignment yields a closed walk of length n through all n
vertices using only edges, i.e. a Hamiltonian cycle; conversely any
Hamiltonian cycle can be rotated to satisfy all clauses.

Edge cases
----------
Graphs with n <= 2 have no Hamiltonian cycle, so we return the
unsatisfiable formula {"num_vars": 0, "clauses": [[]]} (an empty clause is
never satisfied).

The construction uses O(n^2) variables and O(n^3) clauses, so it runs in
polynomial time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2 can never have a simple cycle.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    # Undirected adjacency, both orientations.
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    def var(i, v):
        return i * n + v + 1

    clauses = []

    # Exactly one vertex per position.
    for i in range(n):
        clauses.append([var(i, v) for v in range(n)])
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # Every vertex at exactly one position.
    for v in range(n):
        clauses.append([var(i, v) for i in range(n)])
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, v), -var(j, v)])

    # Fix vertex 0 at position 0.
    clauses.append([var(0, 0)])

    # Consecutive positions must be adjacent in the graph.
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if (u, v) not in edge_set:
                    clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": n * n, "clauses": clauses}
