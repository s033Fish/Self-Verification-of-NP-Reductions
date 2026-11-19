"""Reduction from Hamiltonian Path to SAT.

The source problem is an undirected Hamiltonian Path instance:
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1 and edges are unordered pairs.

The target problem is a CNF SAT instance:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are represented as integers: a positive integer `v` means the
variable `v` is true, a negative integer `-v` means the variable `v` is
false.

We encode the existence of a Hamiltonian path using the classic
polynomial‑time reduction that introduces a boolean variable
`X_{i,j}` (vertex `i` appears at position `j` in the path).  The variable
indices are linearised as ``var_id = i * n + j + 1`` so that they lie in
``1..n*n``.

Constraints encoded as CNF clauses:

1. **Each position is occupied** – for every position `j` the clause
   ``(X_{0,j} ∨ X_{1,j} ∨ … ∨ X_{n-1,j})``.
2. **No position holds two vertices** – for each `j` and each pair
   `i != k` add ``(¬X_{i,j} ∨ ¬X_{k,j})``.
3. **Each vertex appears somewhere** – for every vertex `i` the clause
   ``(X_{i,0} ∨ X_{i,1} ∨ … ∨ X_{i,n-1})``.
4. **No vertex appears twice** – for each `i` and each pair `j != k`
   add ``(¬X_{i,j} ∨ ¬X_{i,k})``.
5. **Adjacency** – if two vertices `i` and `k` are *not* connected by an
   edge, they cannot be consecutive in the path.  For each position
   `j` (0 ≤ j < n‑1) add ``(¬X_{i,j} ∨ ¬X_{k,j+1})``.

Edge cases:
* ``n == 0`` – the Hamiltonian‑Path problem is a definite *no*.
  We return a SAT instance containing an empty clause, which is always
  unsatisfiable.
* ``n == 1`` – always *yes*.  We return a trivially satisfiable formula
  (zero clauses, zero variables).

The construction runs in ``O(n^2 + |E|·n)`` time, which is polynomial in
the size of the input.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a HamiltonianPath instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        {"n": int, "edges": List[List[int]]}

    Returns
    -------
    dict
        {"num_vars": int, "clauses": List[List[int]]}
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case n == 0 : unsatisfiable (empty clause)
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # Edge case n == 1 : trivially satisfiable (no clauses needed)
    if n == 1:
        return {"num_vars": 0, "clauses": []}

    # Build adjacency matrix for quick lookup of non‑edges.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        if 0 <= u < n and 0 <= v < n:
            adj[u][v] = adj[v][u] = True

    # Helper to map (vertex, position) -> variable id (1‑based)
    def var_id(i: int, j: int) -> int:
        return i * n + j + 1

    clauses: List[List[int]] = []

    # 1. Each position occupied by at least one vertex
    for j in range(n):
        clause = [var_id(i, j) for i in range(n)]
        clauses.append(clause)

    # 2. No position holds two vertices (pairwise at most one)
    for j in range(n):
        for i in range(n):
            for k in range(i + 1, n):
                clauses.append([-var_id(i, j), -var_id(k, j)])

    # 3. Each vertex appears in at least one position
    for i in range(n):
        clause = [var_id(i, j) for j in range(n)]
        clauses.append(clause)

    # 4. No vertex appears twice
    for i in range(n):
        for j in range(n):
            for k in range(j + 1, n):
                clauses.append([-var_id(i, j), -var_id(i, k)])

    # 5. Non‑adjacent vertices cannot be consecutive
    for j in range(n - 1):
        for i in range(n):
            for k in range(n):
                if i == k:
                    continue
                if not adj[i][k]:
                    clauses.append([-var_id(i, j), -var_id(k, j + 1)])

    num_vars = n * n
    return {"num_vars": num_vars, "clauses": clauses}

