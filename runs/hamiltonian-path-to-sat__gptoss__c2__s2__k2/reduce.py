"""Reduction from Hamiltonian Path (undirected) to SAT (CNF).

The source problem instance is a dictionary with keys:
    "n": number of vertices (0-indexed vertices 0..n-1)
    "edges": list of undirected edges, each a list [u, v] with u != v.

The target SAT instance format is a dictionary with keys:
    "num_vars": total number of Boolean variables (positive integers 1..m)
    "clauses": list of clauses, each a list of literals. A literal is an
                integer: +v for the variable v being true, -v for false.

The reduction creates a variable x_{i,v} (encoded as a single integer) that
means "vertex v occupies position i in the Hamiltonian path".  Positions are
0‑based and range from 0 to n‑1.  The encoding uses the mapping:

    var_id(i, v) = i * n + v + 1   # variables are 1‑based for SAT

The CNF encodes the following constraints (standard textbook reduction):

1. **Each position contains exactly one vertex**
   - At least one vertex in each position:   (x_{i,0} ∨ x_{i,1} ∨ … ∨ x_{i,n-1})
   - At most one vertex: for all v != w, (¬x_{i,v} ∨ ¬x_{i,w})

2. **Each vertex appears exactly once**
   - At least one position for each vertex: (x_{0,v} ∨ x_{1,v} ∨ … ∨ x_{n-1,v})
   - At most one position: for all i != j, (¬x_{i,v} ∨ ¬x_{j,v})

3. **Consecutive vertices must be adjacent**
   For any non‑edge {u, v} and any consecutive positions i,i+1, we forbid the
   ordering (u at i and v at i+1) and (v at i and u at i+1):
       (¬x_{i,u} ∨ ¬x_{i+1,v})
       (¬x_{i,v} ∨ ¬x_{i+1,u})

Edge cases are handled explicitly:
   * n == 0 → unsatisfiable (return a formula containing the empty clause).
   * n == 1 → trivially satisfiable (force the single variable true).
   * n == 2 → the generic constraints already encode the need for the edge
     between the two vertices; no special handling is required, but the
     construction works for all n >= 1.

The function runs in O(n³) time, which is polynomial in the size of the input
graph.
"""

from typing import List, Dict, Any, Set, Tuple


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    Parameters
    ----------
    instance: dict with keys "n" and "edges" as described above.

    Returns
    -------
    dict representing a SAT formula in the required format.
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Helper to map (position, vertex) -> SAT variable index (1‑based).
    def var_id(pos: int, vertex: int) -> int:
        return pos * n + vertex + 1

    # Edge set for O(1) adjacency checks (undirected).
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        adj.add((a, b))

    # Edge case n == 0 : unsatisfiable. Use a formula with an empty clause.
    if n == 0:
        return {"num_vars": 0, "clauses": [[]]}

    # General case: create variables and clauses.
    num_vars = n * n  # one variable per (position, vertex)
    clauses: List[List[int]] = []

    # 1. Each position has at least one vertex.
    for i in range(n):
        clause = [var_id(i, v) for v in range(n)]
        clauses.append(clause)

    # 1b. Each position has at most one vertex.
    for i in range(n):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var_id(i, v), -var_id(i, w)])

    # 2. Each vertex appears in at least one position.
    for v in range(n):
        clause = [var_id(i, v) for i in range(n)]
        clauses.append(clause)

    # 2b. Each vertex appears in at most one position.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var_id(i, v), -var_id(j, v)])

    # 3. Non‑edges cannot be consecutive.
    for i in range(n - 1):
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                a, b = (u, v) if u < v else (v, u)
                if (a, b) not in adj:
                    # forbid u at i and v at i+1, and the reverse ordering.
                    clauses.append([-var_id(i, u), -var_id(i + 1, v)])
                    clauses.append([-var_id(i, v), -var_id(i + 1, u)])

    # Special handling for n == 1 to keep the formula simple and avoid
    # redundant clauses that could reference variables beyond the count.
    if n == 1:
        # Force the single variable true.
        clauses = [[var_id(0, 0)]]
        num_vars = 1

    return {"num_vars": num_vars, "clauses": clauses}

