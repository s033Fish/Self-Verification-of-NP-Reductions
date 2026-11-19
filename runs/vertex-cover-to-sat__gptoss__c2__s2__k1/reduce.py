"""Reduction from Vertex Cover to SAT.

The source problem (VertexCover) instance format is:
    {"n": int, "edges": [[u, v], ...], "k": int}
where vertices are 0..n-1.

The target problem (Sat) instance format is:
    {"num_vars": int, "clauses": [[literal, ...], ...]}
Literals are represented as signed integers: +v for variable v true,
‑v for variable v false. Variables are numbered from 1.

We use the classic encoding that introduces a variable x_{i,p} meaning
"vertex i occupies position p in the cover" for p in 1..k.  The formula
ensures:
  * Every position 1..k is occupied by some vertex.
  * No vertex occupies two different positions.
  * For every edge (u, v) at least one of its endpoints appears in the
    cover (i.e., occupies some position).

If a vertex cover of size ≤ k exists, we can extend it to exactly k by
adding arbitrary unused vertices, satisfying the constraints.  Conversely,
any satisfying assignment corresponds to a set of at most k vertices that
covers all edges.

Edge‑case handling:
  * k < 0  -> unsatisfiable (return a formula containing an empty clause).
  * k >= n -> trivially satisfiable (return a formula with no clauses).

The reduction runs in polynomial time O(n·k + |E|·k).
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        VertexCover instance with keys "n", "edges", and "k".

    Returns
    -------
    dict
        SAT instance in the required format.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases -----------------------------------------------------------
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}
    if k >= n:
        # Any graph is covered by all vertices, so return a trivially
        # satisfiable formula (no clauses).
        return {"num_vars": 0, "clauses": []}

    # Mapping (vertex, position) -> variable index (1‑based)
    # variable index = vertex * k + position (1‑based positions)
    def var(i: int, p: int) -> int:
        return i * k + p  # p in 1..k, i in 0..n-1

    total_vars = n * k
    clauses: List[List[int]] = []

    # 1. Each position p must be occupied by at least one vertex.
    for p in range(1, k + 1):
        clause = [var(i, p) for i in range(n)]
        clauses.append(clause)

    # 2. No vertex occupies two different positions (at most one).
    for i in range(n):
        for p in range(1, k + 1):
            for q in range(p + 1, k + 1):
                clauses.append([-var(i, p), -var(i, q)])

    # 3. Edge coverage: for each edge (u, v) at least one endpoint is in the cover.
    for u, v in edges:
        clause = []
        for p in range(1, k + 1):
            clause.append(var(u, p))
            clause.append(var(v, p))
        clauses.append(clause)

    return {"num_vars": total_vars, "clauses": clauses}

