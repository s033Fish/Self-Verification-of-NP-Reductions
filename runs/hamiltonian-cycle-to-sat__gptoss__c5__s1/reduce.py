"""Reduction from Hamiltonian Cycle (undirected) to SAT.

The reduction follows the classic encoding using variables x_{v,i} meaning
"vertex *v* occupies position *i* in the Hamiltonian cycle".  Positions are
0‑based and range from 0 to n‑1.  Variables are numbered from 1 as required
by the SAT problem definition.

Constraints encoded as CNF clauses:

1. **Each position is occupied by at least one vertex** – a clause with all
   positive literals x_{v,i} for a fixed i.
2. **No position contains two different vertices** – for each position i and
   each unordered pair of distinct vertices u < v a clause (¬x_{u,i} ∨ ¬x_{v,i}).
3. **Each vertex appears in at least one position** – a clause with all
   positive literals x_{v,i} for a fixed vertex v.
4. **No vertex appears in two different positions** – for each vertex v and
   each unordered pair of distinct positions i < j a clause (¬x_{v,i} ∨ ¬x_{v,j}).
5. **Consecutive vertices must be adjacent** – for each position i and each
   ordered pair (u, v) that is *not* an edge of the graph we add a clause
   (¬x_{u,i} ∨ ¬x_{v,i+1}) where i+1 is taken modulo n.

If the input graph has n ≤ 2 the answer is always *no*.  To preserve the
correctness of the reduction we output an obviously unsatisfiable SAT
instance – a formula containing an empty clause.

The function runs in polynomial time in the size of the input graph.
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple, Set

from problems import HamiltonianCycle, Sat


def _var_id(v: int, i: int, n: int) -> int:
    """Return the SAT variable number for vertex *v* at position *i*.

    Variables are numbered starting at 1, so we add 1 to the zero‑based index.
    """
    return v * n + i + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to an equivalent SAT instance.

    The returned dictionary follows the format required by ``Sat.validate``:
    ``{"num_vars": m, "clauses": [[l1, l2, ...], ...]}`` where each literal is
    an integer ``+v`` for a positive literal and ``-v`` for a negated literal.
    """
    # Validate source instance first.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case: n <= 2 -> always NO. Return unsatisfiable formula.
    if n <= 2:
        # One variable is enough; an empty clause makes the formula unsat.
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for O(1) edge checks.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        adj.add((u, v))
        adj.add((v, u))

    clauses: List[List[int]] = []

    # 1. Each position i has at least one vertex.
    for i in range(n):
        clause = [_var_id(v, i, n) for v in range(n)]
        clauses.append(clause)

    # 2. No position contains two distinct vertices.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var_id(u, i, n), -_var_id(v, i, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var_id(v, i, n) for i in range(n)]
        clauses.append(clause)

    # 4. No vertex appears in two positions.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(v, i, n), -_var_id(v, j, n)])

    # 5. Non‑edges cannot be consecutive in the cycle.
    for i in range(n):
        next_i = (i + 1) % n
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if (u, v) not in adj:
                    clauses.append([-_var_id(u, i, n), -_var_id(v, next_i, n)])

    num_vars = n * n
    # Validate the produced SAT instance before returning.
    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

