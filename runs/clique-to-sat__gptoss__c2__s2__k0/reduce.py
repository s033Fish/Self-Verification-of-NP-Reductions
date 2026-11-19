"""Reduction from Clique to SAT.

The source problem (Clique) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem (Sat) instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}

The reduction follows the classic polynomial‑time encoding of the CLIQUE
problem into a Boolean formula in conjunctive normal form.

For each vertex ``i`` (0‑based) and each position ``p`` in the potential
clique (also 0‑based, ``0 ≤ p < k``) we introduce a Boolean variable
``x_{i,p}`` that is true iff vertex ``i`` occupies position ``p`` of the
clique.  Variables are numbered from ``1`` as required by the SAT format:

    var(i, p) = i * k + p + 1

The CNF consists of four families of clauses:

1. **Each position is occupied by at least one vertex** – for every ``p``
   we add the clause ``(x_{0,p} ∨ x_{1,p} ∨ … ∨ x_{n‑1,p})``.

2. **No position contains two different vertices** – for every ``p`` and
   every pair ``i < j`` we add ``(¬x_{i,p} ∨ ¬x_{j,p})``.

3. **No vertex appears in two positions** – for every vertex ``i`` and
   every pair ``p < q`` we add ``(¬x_{i,p} ∨ ¬x_{i,q})``.

4. **Selected vertices must be pairwise adjacent** – for every non‑edge
   ``{i, j}`` (i.e., ``i != j`` and ``{i, j}`` is not in the edge set) and
   for all positions ``p, q`` we add ``(¬x_{i,p} ∨ ¬x_{j,q})``.  This
   guarantees that two non‑adjacent vertices cannot both be chosen, no
   matter which positions they occupy.

Edge‑case handling:
* ``k <= 0`` – always a YES instance.  We output a trivially satisfiable
  SAT formula: zero variables and zero clauses.
* ``k == 1`` and ``n >= 1`` – also always YES; the same trivial formula
  suffices.
* ``k > n`` – always NO.  We output an unsatisfiable formula consisting
  of a single empty clause.

The function runs in time polynomial in ``n`` and ``k`` (specifically
``O(n^2 * k^2)``), satisfying the required complexity bound.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

    The returned SAT instance is a dict with keys ``"num_vars"`` and
    ``"clauses"`` as described in the module docstring.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling ---------------------------------------------------
    if k <= 0:
        # Always YES – empty formula is satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 1 and n >= 1:
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Always NO – a single empty clause makes the formula unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency set for quick non‑edge queries.
    adjacency: Set[frozenset[int]] = {frozenset(edge) for edge in edges}

    def var(i: int, p: int) -> int:
        """Map vertex i and position p to a SAT variable number (1‑based)."""
        return i * k + p + 1

    clauses: List[List[int]] = []

    # 1. Each position must be occupied by at least one vertex.
    for p in range(k):
        clause = [var(i, p) for i in range(n)]
        clauses.append(clause)

    # 2. No position contains two different vertices.
    for p in range(k):
        for i in range(n):
            vi = var(i, p)
            for j in range(i + 1, n):
                vj = var(j, p)
                clauses.append([-vi, -vj])

    # 3. No vertex appears in two positions.
    for i in range(n):
        for p in range(k):
            vp = var(i, p)
            for q in range(p + 1, k):
                vq = var(i, q)
                clauses.append([-vp, -vq])

    # 4. Non‑adjacent vertices cannot both be selected.
    # Iterate over unordered pairs of distinct vertices that are NOT edges.
    for i in range(n):
        for j in range(i + 1, n):
            if frozenset((i, j)) in adjacency:
                continue  # they are adjacent, no restriction needed
            # For every pair of positions (p, q) add the clause.
            for p in range(k):
                vi = var(i, p)
                for q in range(k):
                    vj = var(j, q)
                    clauses.append([-vi, -vj])

    num_vars = n * k
    return {"num_vars": num_vars, "clauses": clauses}

