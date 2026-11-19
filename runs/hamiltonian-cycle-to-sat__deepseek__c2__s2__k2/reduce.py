"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
For a graph with n >= 3 vertices we introduce a boolean variable

    x[v, i]   (1-indexed as v * n + i + 1)

meaning "vertex v is the i-th vertex of the cycle" (positions 0..n-1,
with position n-1 wrapping around to position 0).

The CNF contains:

  1. For every position i, the clause [x[0,i], ..., x[n-1,i]]
     (at least one vertex occupies position i).
  2. For every position i and every pair u < v, the clause
     [-x[u,i], -x[v,i]]  (at most one vertex occupies position i).
  3. For every vertex v, the clause [x[v,0], ..., x[v,n-1]]
     (vertex v occurs somewhere).
  4. For every vertex v and every pair i < j, the clause
     [-x[v,i], -x[v,j]]  (vertex v occurs at most once).
  5. For every position i, every ordered pair (u, v) with u != v and
     {u, v} not an edge, the clause [-x[u,i], -x[v,(i+1) mod n]]
     (consecutive cycle vertices must be joined by an edge).

Clauses 1-4 force a bijection between vertices and positions.  Clause 5
then forces consecutive positions to be adjacent, so a satisfying
assignment is exactly a Hamiltonian cycle and vice versa.

Graphs with n <= 2 can never have a Hamiltonian cycle, so they are
mapped to the unsatisfiable formula {"num_vars": 0, "clauses": [[]]}.

The formula has O(n^2) variables and O(n^3) clauses, and is built in
polynomial time.  No solver is invoked.
"""


def _unsatisfiable():
    return {"num_vars": 0, "clauses": [[]]}


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # A simple graph on fewer than 3 vertices has no cycle.
    if n < 3:
        return _unsatisfiable()

    # x[v, i] -> variable v * n + i + 1
    def var(v, i):
        return v * n + i + 1

    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    clauses = []

    # 1. At least one vertex per position.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. At most one vertex per position.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(u, i), -var(v, i)])

    # 3. Each vertex occurs at least once.
    for v in range(n):
        clauses.append([var(v, i) for i in range(n)])

    # 4. Each vertex occurs at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 5. Consecutive positions must be adjacent.
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u != v and (u, v) not in edge_set:
                    clauses.append([-var(u, i), -var(v, j)])

    return {"num_vars": n * n, "clauses": clauses}
