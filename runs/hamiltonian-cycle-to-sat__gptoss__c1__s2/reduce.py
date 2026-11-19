"""Reduction from Hamiltonian Cycle to SAT.

The source problem is an undirected Hamiltonian Cycle instance:
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1 and each edge appears only once.

The target problem is SAT in CNF form:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are signed integers: +v means variable v is true, -v means false.

We implement the classic polynomial‑time reduction using variables
``x_{i,v}`` meaning "vertex *v* occupies position *i* in the Hamiltonian
cycle" (positions are 0..n-1).  There are n² variables, numbered
``id = i * n + v + 1`` (SAT variables are 1‑based).

The CNF encodes the following constraints:

1. **Each position contains at least one vertex**
   (x_{i,0} ∨ x_{i,1} ∨ … ∨ x_{i,n‑1})

2. **Each position contains at most one vertex**
   (¬x_{i,u} ∨ ¬x_{i,v}) for all u ≠ v.

3. **Each vertex appears in at least one position**
   (x_{0,v} ∨ x_{1,v} ∨ … ∨ x_{n‑1,v})

4. **Each vertex appears at most once**
   (¬x_{i,v} ∨ ¬x_{j,v}) for all i ≠ j.

5. **Consecutive vertices must be adjacent**.  For every position i and
   every unordered pair of distinct vertices (u, v) that is **not** an
   edge of the graph, we forbid the assignment where u is at position i
   and v is at position (i+1) mod n.  This yields the clause
   (¬x_{i,u} ∨ ¬x_{i+1,v}).  Because the graph is undirected we also add
   (¬x_{i,v} ∨ ¬x_{i+1,u}).

Edge cases:
* For n ≤ 2 the Hamiltonian Cycle problem is always a NO instance.  We
  return an UNSAT formula by providing a single empty clause ``[]``.
* For n = 0 the same handling applies.

The reduction runs in O(n² + n·|E̅|) time, which is polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set, Tuple

def _var_id(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position *i* and vertex *v*.

    SAT variables are 1‑based, so we add 1 to the zero‑based index.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` as described in the
        problem statement.

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case: n <= 2 -> always NO. Produce an unsatisfiable formula.
    if n <= 2:
        return {"num_vars": 1, "clauses": [[]]}  # empty clause makes it UNSAT

    # Build adjacency set for O(1) edge lookup.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u == v:
            continue  # ignore self‑loops (they never help a Hamiltonian cycle)
        a, b = (u, v) if u < v else (v, u)
        adj.add((a, b))

    clauses: List[List[int]] = []
    num_vars = n * n

    # 1. Each position has at least one vertex.
    for i in range(n):
        clause = [_var_id(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. Each position has at most one vertex.
    for i in range(n):
        for u in range(n):
            for v in range(u + 1, n):
                clauses.append([-_var_id(i, u, n), -_var_id(i, v, n)])

    # 3. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var_id(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 4. Each vertex appears at most once.
    for v in range(n):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, v, n), -_var_id(j, v, n)])

    # 5. Edge constraints for consecutive positions.
    # Pre‑compute the set of non‑edges (unordered pairs of distinct vertices).
    non_edges: List[Tuple[int, int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in adj:
                non_edges.append((u, v))

    for i in range(n):
        nxt = (i + 1) % n
        for u, v in non_edges:
            # forbid u at i and v at nxt
            clauses.append([-_var_id(i, u, n), -_var_id(nxt, v, n)])
            # forbid v at i and u at nxt (undirected)
            clauses.append([-_var_id(i, v, n), -_var_id(nxt, u, n)])

    return {"num_vars": num_vars, "clauses": clauses}


__all__ = ["reduce"]

