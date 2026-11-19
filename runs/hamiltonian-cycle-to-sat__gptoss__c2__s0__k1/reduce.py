"""Reduction from Hamiltonian Cycle (undirected) to SAT (CNF).

The source problem instance is a dictionary with keys:
    - "n": number of vertices (vertices are 0..n-1)
    - "edges": list of undirected edges, each edge is a two‑element list
      [u, v] with u != v.  The edge [u, v] is considered identical to [v, u]
      and will appear at most once.

The target SAT instance is a dictionary with keys:
    - "num_vars": total number of Boolean variables (numbered 1..m)
    - "clauses": list of clauses, each clause is a list of literals.
      A positive integer v denotes the literal "v is true" and a negative
      integer -v denotes "v is false".

The reduction creates a variable x_{i,p} meaning that vertex *i* occupies
position *p* in the Hamiltonian cycle (positions are 0..n-1).  Variables are
encoded as a single integer id = i * n + p + 1, ensuring a contiguous range
1..n*n.

Constraints encoded as CNF clauses:
1. **Each position is occupied by exactly one vertex**
   - At least one vertex in each position:  (x_{0,p} ∨ x_{1,p} ∨ … ∨ x_{n-1,p})
   - At most one vertex: for all i < j, (¬x_{i,p} ∨ ¬x_{j,p})

2. **Each vertex appears in exactly one position**
   - At least one position for each vertex: (x_{i,0} ∨ … ∨ x_{i,n-1})
   - At most one position: for all p < q, (¬x_{i,p} ∨ ¬x_{i,q})

3. **Adjacency constraint** – non‑edges cannot be consecutive in the cycle.
   For every unordered pair {i, j} that is *not* an edge and for every
   position p, we forbid i at p and j at p+1 (mod n) as well as the symmetric
   ordering:
       (¬x_{i,p} ∨ ¬x_{j,(p+1) mod n})
       (¬x_{j,p} ∨ ¬x_{i,(p+1) mod n})

If n ≤ 2 the source instance is always a *no* instance (by the problem
statement).  To reflect this we output an unsatisfiable SAT formula – a
single empty clause.

The construction runs in O(n³) time and produces O(n²) variables and
O(n³) clauses, which is polynomial.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    Parameters
    ----------
    instance:
        Dictionary with keys "n" and "edges" as described above.

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.Sat``.
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case: n <= 2 – always a NO instance.
    if n <= 2:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for quick lookup.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        if 0 <= u < n and 0 <= v < n:
            adj[u][v] = adj[v][u] = True

    # Helper to map (i, p) -> variable id (1‑based).
    def var(i: int, p: int) -> int:
        return i * n + p + 1

    clauses: List[List[int]] = []

    # 1. Each position has at least one vertex.
    for p in range(n):
        clause = [var(i, p) for i in range(n)]
        clauses.append(clause)

    # 1b. Each position has at most one vertex (pairwise).
    for p in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var(i, p), -var(j, p)])

    # 2. Each vertex appears in at least one position.
    for i in range(n):
        clause = [var(i, p) for p in range(n)]
        clauses.append(clause)

    # 2b. Each vertex appears in at most one position (pairwise).
    for i in range(n):
        for p in range(n):
            for q in range(p + 1, n):
                clauses.append([-var(i, p), -var(i, q)])

    # 3. Non‑edges cannot be consecutive.
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i][j]:
                for p in range(n):
                    nxt = (p + 1) % n
                    # i at p and j at nxt cannot both be true
                    clauses.append([-var(i, p), -var(j, nxt)])
                    # j at p and i at nxt cannot both be true
                    clauses.append([-var(j, p), -var(i, nxt)])

    num_vars = n * n
    return {"num_vars": num_vars, "clauses": clauses}

