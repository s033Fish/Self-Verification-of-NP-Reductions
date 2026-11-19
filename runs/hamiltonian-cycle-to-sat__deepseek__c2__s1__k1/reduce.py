"""Polynomial-time reduction from Hamiltonian Cycle (undirected) to SAT.

Encoding
--------
A Hamiltonian cycle is a cyclic ordering of all n vertices in which every
pair of cyclically consecutive vertices is joined by an edge.

For n >= 3 we fix vertex 0 at position 0 (every cycle can be rotated so that
it starts there).  For the remaining positions 1..n-1 and the remaining
vertices 1..n-1 we introduce a boolean variable

    x(i, v)  ==  "vertex v is the i-th vertex of the cycle".

The clauses enforce:

  * every position 1..n-1 holds at least one vertex, and at most one;
  * every vertex 1..n-1 occurs at least once, and at most once;
  * position 0 (vertex 0) and position 1 are joined by an edge;
  * positions i and i+1 (1 <= i <= n-2) are joined by an edge;
  * position n-1 and position 0 (vertex 0) are joined by an edge.

Together these say exactly that the vertices can be arranged in a cyclic
order whose consecutive pairs are edges, i.e. that a Hamiltonian cycle
exists.  The construction uses O(n^2) variables and O(n^3) clauses, so it
runs in polynomial time.

Graphs with n <= 2 can never have a Hamiltonian cycle, so they are mapped to
the trivially unsatisfiable formula containing the empty clause.
"""


def reduce(instance):
    """Reduce a Hamiltonian Cycle instance to a SAT instance."""
    n = instance["n"]
    edges = instance["edges"]

    # A simple graph needs at least three vertices to contain a cycle.
    if n <= 2:
        return {"num_vars": 0, "clauses": [[]]}

    # Undirected adjacency, stored in both directions.
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    m = n - 1  # number of unfixed positions / vertices

    def var(i, v):
        # i, v are 1-based indices in 1..m.
        return (i - 1) * m + (v - 1) + 1

    num_vars = m * m
    clauses = []

    # Every position holds at least one vertex.
    for i in range(1, m + 1):
        clauses.append([var(i, v) for v in range(1, m + 1)])

    # Every position holds at most one vertex.
    for i in range(1, m + 1):
        for v in range(1, m + 1):
            for w in range(v + 1, m + 1):
                clauses.append([-var(i, v), -var(i, w)])

    # Every vertex appears at least once.
    for v in range(1, m + 1):
        clauses.append([var(i, v) for i in range(1, m + 1)])

    # Every vertex appears at most once.
    for v in range(1, m + 1):
        for i in range(1, m + 1):
            for j in range(i + 1, m + 1):
                clauses.append([-var(i, v), -var(j, v)])

    # Edge between position 0 (vertex 0) and position 1.
    for v in range(1, m + 1):
        if (0, v) not in edge_set:
            clauses.append([-var(1, v)])

    # Edges between consecutive positions i and i+1 for i = 1..n-2.
    for i in range(1, m):
        for u in range(1, m + 1):
            for v in range(1, m + 1):
                if u != v and (u, v) not in edge_set:
                    clauses.append([-var(i, u), -var(i + 1, v)])

    # Edge between the last position and position 0 (vertex 0).
    for v in range(1, m + 1):
        if (v, 0) not in edge_set:
            clauses.append([-var(m, v)])

    return {"num_vars": num_vars, "clauses": clauses}
