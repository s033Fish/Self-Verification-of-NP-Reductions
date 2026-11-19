"""Polynomial-time reduction from Clique to SAT.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
For k <= 0 the answer is always yes, so return the trivially satisfiable
formula with no clauses.

For k > n the answer is always no, so return a formula containing the empty
clause (which can never be satisfied).

Otherwise 1 <= k <= n.  Introduce a variable x_{i,j} for every vertex
i in 0..n-1 and every position j in 1..k, meaning "vertex i is the j-th
vertex of the clique".  Number them as x_{i,j} = i*k + j + 1, so there are
n*k variables.  Add clauses:

  * For each position j: [x_{0,j}, ..., x_{n-1,j}]
        every position is occupied by some vertex.
  * For each position j and vertices i < i': [-x_{i,j}, -x_{i',j}]
        at most one vertex per position.
  * For each vertex i and positions j < j': [-x_{i,j}, -x_{i,j'}]
        a vertex occupies at most one position.
  * For each non-edge {i, i'} and positions j != j':
        [-x_{i,j}, -x_{i',j'}]
        two non-adjacent vertices cannot both be in the clique.

A satisfying assignment selects exactly k distinct, pairwise adjacent
vertices, i.e. a k-clique.  Conversely any k-clique yields a satisfying
assignment.  Since any subset of a clique is a clique, a clique of size
exactly k exists iff a clique of size at least k exists (for k <= n).
The number of clauses is O(n^2 k^2), so the reduction is polynomial time.
"""


def _var(i, j, k):
    """Variable index (1-based) for vertex i at position j (0-based)."""
    return i * k + j + 1


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the Clique specification.
    if k <= 0:
        # Always yes: the empty CNF is satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Always no: the empty clause is unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    # 1 <= k <= n.
    num_vars = n * k
    clauses = []

    # Every position holds at least one vertex.
    for j in range(k):
        clauses.append([_var(i, j, k) for i in range(n)])

    # At most one vertex per position.
    for j in range(k):
        for i in range(n):
            for i2 in range(i + 1, n):
                clauses.append([-_var(i, j, k), -_var(i2, j, k)])

    # A vertex occupies at most one position.
    for i in range(n):
        for j in range(k):
            for j2 in range(j + 1, k):
                clauses.append([-_var(i, j, k), -_var(i, j2, k)])

    # Non-adjacent vertices cannot both be in the clique.
    adjacent = set()
    for u, v in edges:
        adjacent.add((u, v))
        adjacent.add((v, u))
    for i in range(n):
        for i2 in range(i + 1, n):
            if (i, i2) in adjacent:
                continue
            for j in range(k):
                for j2 in range(k):
                    if j == j2:
                        continue
                    clauses.append([-_var(i, j, k), -_var(i2, j2, k)])

    return {"num_vars": num_vars, "clauses": clauses}
