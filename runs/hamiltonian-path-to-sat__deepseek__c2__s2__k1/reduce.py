"""Polynomial-time reduction from Hamiltonian Path (undirected, any endpoints)
to SAT (CNF satisfiability).

Source instance format (HamiltonianPath):
    {"n": n, "edges": [[u, v], ...]}
Target instance format (Sat):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce a boolean variable x_{v,i} for every vertex v in 0..n-1 and every
position i in 0..n-1, meaning "vertex v is the i-th vertex of the path".
Variable number is v * n + i + 1, so there are n * n variables.

Clauses:
  1. For each position i: [x_{0,i}, ..., x_{n-1,i}]
     (each position holds at least one vertex).
  2. For each vertex v and each pair of positions i < j:
     [-x_{v,i}, -x_{v,j}]
     (each vertex is used at most once).
  3. For each position i in 0..n-2 and each ordered pair u != v that is NOT
     an edge: [-x_{u,i}, -x_{v,i+1}]
     (consecutive vertices must be joined by an edge).

There are n position clauses, O(n^3) at-most-once clauses and O(n^3)
adjacency clauses, so the reduction is polynomial.

Correctness
-----------
(=>) A Hamiltonian path v_0, ..., v_{n-1} satisfies the formula by setting
x_{v_i,i} true. Each position has a vertex, no vertex repeats, and every
consecutive pair is an edge, so all clauses hold.

(<=) A satisfying assignment has at least one true literal in every position
clause, and the at-most-once clauses force each vertex to appear in at most
one position. Hence at least n true variables and at most n true variables,
so exactly one variable x_{v_i,i} is true for each position i, and the v_i
are all distinct. Clause group 3 guarantees (v_i, v_{i+1}) is an edge for all
i, so v_0, ..., v_{n-1} is a Hamiltonian path.

Edge cases
----------
n = 0: no path exists, so return an unsatisfiable formula (one empty clause).
n = 1: the single position clause [x_{0,0}] is satisfiable -> yes.
n = 2: satisfiable exactly when the edge [0, 1] is present.
"""


def reduce(instance):
    """Return a SAT instance that is satisfiable iff the input graph has a
    Hamiltonian path."""
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: Hamiltonian Path is "no"; emit an unsatisfiable formula.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    def var(v, i):
        # Variable 1..n*n for "vertex v is at position i".
        return v * n + i + 1

    # Normalise the undirected edges into a set of directed arcs.
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))

    clauses = []

    # 1. Every position is occupied by at least one vertex.
    for i in range(n):
        clauses.append([var(v, i) for v in range(n)])

    # 2. Every vertex is used at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(v, i), -var(v, j)])

    # 3. Consecutive positions must be joined by an edge.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u != v and (u, v) not in edge_set:
                    clauses.append([-var(u, i), -var(v, i + 1)])

    return {"num_vars": n * n, "clauses": clauses}
