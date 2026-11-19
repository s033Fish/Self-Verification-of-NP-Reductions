"""Reduction from Clique to SAT.

The source problem is **Clique** with instances of the form:

    {"n": n, "edges": [[u, v], ...], "k": k}

The target problem is **SAT** (CNF) with instances of the form:

    {"num_vars": m, "clauses": [[literal, ...], ...]}

The reduction creates a CNF formula that is satisfiable iff the input
graph contains a clique of size at least ``k``.  The construction follows
the classic textbook reduction using variables ``x_{i,v}`` that indicate
that vertex ``v`` occupies position ``i`` in the (ordered) clique.

Variable numbering:
    var(i, v) = i * n + v + 1          # 1‑based as required by the SAT format

The clauses enforce:
    1. Each position i (0 ≤ i < k) is occupied by *some* vertex.
    2. No position contains two different vertices.
    3. No vertex appears in two different positions.
    4. Non‑edges cannot both be chosen (i.e., for any pair of vertices
       without an edge, they cannot simultaneously occupy two positions).

Edge cases are handled explicitly to keep the output small:
    * k ≤ 0 – always a YES instance → return a trivially satisfiable formula
      (no clauses).
    * k = 1 and n ≥ 1 – also always YES → return an empty formula.
    * k > n – always NO → return a formula containing a single empty clause
      which is unsatisfiable.

The function runs in time polynomial in ``n`` and ``k``.
"""

from typing import List, Dict, Any, Set, Tuple


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A SAT instance in the required format.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling ---------------------------------------------------
    if k <= 0:
        # Empty formula is always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        # Any single vertex forms a 1‑clique when n >= 1 (the definition of the
        # source problem guarantees n >= 0).  Return a trivially satisfiable
        # instance.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Unsatisfiable: a formula with an empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # Normal case ----------------------------------------------------------
    # Build a set for quick edge existence checks.
    edge_set: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Helper to compute variable index (1‑based).
    def var(i: int, v: int) -> int:
        return i * n + v + 1

    clauses: List[List[int]] = []

    # 1. Each position i must contain at least one vertex.
    for i in range(k):
        clause = [var(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. At most one vertex per position (pairwise mutual exclusion).
    for i in range(k):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-var(i, v), -var(i, w)])

    # 3. No vertex appears in two different positions.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var(i, v), -var(j, v)])

    # 4. Non‑edges cannot both be selected.
    # Iterate over unordered pairs of vertices that are NOT edges.
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) in edge_set:
                continue  # they are adjacent, no restriction needed
            # For every ordered pair of positions (i, j) we forbid selecting
            # u at i and v at j simultaneously.
            for i in range(k):
                for j in range(k):
                    clauses.append([-var(i, u), -var(j, v)])
                    clauses.append([-var(i, v), -var(j, u)])

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}

