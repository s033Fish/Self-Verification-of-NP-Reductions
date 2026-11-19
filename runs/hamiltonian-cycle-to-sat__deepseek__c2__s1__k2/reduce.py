"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
Let the source graph have ``n`` vertices and edge set ``E``.  For ``n >= 3``
introduce a boolean variable ``x[i][v]`` for every position ``i`` in
``0..n-1`` and every vertex ``v`` in ``0..n-1``.  The intended meaning is
"vertex ``v`` is the ``i``-th vertex of the cycle".

The CNF contains the following clauses:

1. At least one vertex per position:
       (x[i][0] or x[i][1] or ... or x[i][n-1])          for every i
2. At most one vertex per position:
       (~x[i][u] or ~x[i][v])                            for every i, u < v
3. At least one position per vertex:
       (x[0][v] or x[1][v] or ... or x[n-1][v])          for every v
4. At most one position per vertex:
       (~x[i][v] or ~x[j][v])                            for every v, i < j
5. Consecutive positions must be joined by an edge.  For every position i
   with next position j = (i+1) mod n and every ordered pair of distinct
   vertices (u, v) such that {u, v} is not an edge:
       (~x[i][u] or ~x[j][v])

Clauses 1-4 force the true variables to describe a permutation of the
vertices over the positions.  Clause 5 then requires every consecutive pair
(including the wrap-around pair) to be an edge, i.e. exactly a Hamiltonian
cycle.  Conversely any Hamiltonian cycle yields the satisfying assignment
that puts the cycle's vertices in order.

The formula has ``n^2`` variables and ``O(n^3)`` clauses, so the reduction
runs in polynomial time.  For ``n <= 2`` a simple graph can never have a
Hamiltonian cycle, so the constant unsatisfiable formula ``[[]]`` is
returned.
"""


def reduce(instance):
    """Reduce a Hamiltonian Cycle instance to a SAT instance.

    ``instance`` is ``{"n": n, "edges": [[u, v], ...]}`` and the result is
    ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.
    """
    n = instance["n"]
    edges = instance["edges"]

    # A simple graph on fewer than 3 vertices has no cycle at all.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    # Normalised, undirected edge set.
    edge_set = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    def var(position, vertex):
        # Variables are 1..n*n.
        return position * n + vertex + 1

    clauses = []

    # 1. Each position holds at least one vertex.
    for i in range(n):
        clauses.append([var(i, v) for v in range(n)])

    # 2. Each position holds at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var(i, u), -var(i, v)])

    # 3. Each vertex occupies at least one position.
    for v in range(n):
        clauses.append([var(i, v) for i in range(n)])

    # 4. Each vertex occupies at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, v), -var(j, v)])

    # 5. Consecutive positions must be connected by an edge.
    for i in range(n):
        j = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                a, b = (u, v) if u < v else (v, u)
                if (a, b) not in edge_set:
                    clauses.append([-var(i, u), -var(j, v)])

    return {"num_vars": n * n, "clauses": clauses}
