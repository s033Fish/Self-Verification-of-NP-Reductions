"""Reduction from Hamiltonian Cycle (undirected) to SAT.

The source problem instance is a dictionary with keys:
    - "n": number of vertices (vertices are 0..n-1)
    - "edges": list of undirected edges, each represented as [u, v]

The target problem is SAT in CNF.  An instance is a dictionary with keys:
    - "num_vars": total number of Boolean variables (numbered 1..m)
    - "clauses": list of clauses, each clause is a list of literals.
      A literal is an integer ``+v`` (meaning variable v is true) or ``-v``
      (meaning variable v is false).  The empty clause ``[]`` is unsatisfiable.

The reduction follows the classic textbook construction:

*Variables*
    For each position ``i`` in the Hamiltonian cycle (0 ≤ i < n) and each
    vertex ``v`` (0 ≤ v < n) we introduce a Boolean variable ``x_{i,v}``
    which is true iff vertex ``v`` occupies position ``i`` in the cycle.
    Variables are numbered ``var_id = i * n + v + 1`` (SAT uses 1‑based ids).

*Clauses*
    1. **Each position contains at least one vertex**:
       ``(x_{i,0} ∨ x_{i,1} ∨ ... ∨ x_{i,n-1})`` for every position ``i``.
    2. **No position contains two different vertices**:
       ``(¬x_{i,u} ∨ ¬x_{i,v})`` for every position ``i`` and every ``u < v``.
    3. **Each vertex appears in at least one position**:
       ``(x_{0,v} ∨ x_{1,v} ∨ ... ∨ x_{n-1,v})`` for every vertex ``v``.
    4. **No vertex appears in two positions**:
       ``(¬x_{i,v} ∨ ¬x_{j,v})`` for every vertex ``v`` and every ``i < j``.
    5. **Adjacency constraints** – consecutive positions must be connected by
       an edge.  For each position ``i`` (including the wrap‑around from the
       last to the first) and for each pair of vertices ``u, v`` that are **not**
       adjacent in the input graph we add the clause
       ``(¬x_{i,u} ∨ ¬x_{i+1 mod n, v})``.

If ``n <= 2`` the Hamiltonian‑cycle problem is defined to be a NO instance.
In that case we return a trivially unsatisfiable SAT instance consisting of a
single empty clause.

The function runs in polynomial time (O(n³) clauses in the worst case) and
produces a SAT instance that is satisfiable exactly when the original graph
has a Hamiltonian cycle.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary ``{"n": int, "edges": List[List[int]]}`` describing an
        undirected simple graph.

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py``.
    """

    n = instance.get("n", 0)
    edges = instance.get("edges", [])

    # Edge case: n <= 2 -> always NO. Return an unsatisfiable SAT formula.
    if n <= 2:
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for O(1) look‑ups.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        if 0 <= u < n and 0 <= v < n:
            adj[u][v] = adj[v][u] = True

    # Helper to map (position, vertex) -> variable id (1‑based).
    def var_id(pos: int, vertex: int) -> int:
        return pos * n + vertex + 1

    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [var_id(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. No position contains two different vertices.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-var_id(i, u), -var_id(i, v)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [var_id(i, v) for i in range(n)]
        clauses.append(clause)

    # 4. No vertex appears in two positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-var_id(i, v), -var_id(j, v)])

    # 5. Edge constraints for consecutive positions (including wrap‑around).
    for i in range(n):
        next_i = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if not adj[u][v]:
                    clauses.append([-var_id(i, u), -var_id(next_i, v)])

    num_vars = n * n
    return {"num_vars": num_vars, "clauses": clauses}

