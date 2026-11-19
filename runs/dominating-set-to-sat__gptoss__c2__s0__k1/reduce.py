"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) instance format is:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are numbered 0..n-1, edges are undirected and k is an
integer.  The question is whether there exists a dominating set of size
at most k.

The target problem (Sat) instance format is:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
where variables are 1..m and a literal is +v (represented by the
positive integer v) for true or -v (negative integer) for false.

The reduction works as follows (polynomial time):

* For each position p = 0..k-1 we introduce a *selection* variable for
  every vertex v = 0..n (the extra vertex n is a dummy representing "no
  vertex chosen" for this position).  Variable y_{p,v} is true iff the
  p‑th slot of the dominating set is assigned vertex v.  The total number
  of variables is k·(n+1).

* Constraints encoded as SAT clauses:
  1. **Exactly one vertex per position** – we enforce at least one
     vertex (including the dummy) with a clause containing all y_{p,*}
     variables, and we forbid two different vertices being chosen for
     the same position by pairwise negative clauses.
  2. **A real vertex cannot occupy two positions** – for each real
     vertex v (0..n-1) and each pair of positions p<q we add a clause
     (¬y_{p,v} ∨ ¬y_{q,v}).
  3. **Domination** – for every vertex v the formula must contain a
     clause that is satisfied if v itself or one of its neighbours is
     selected in any position.  Concretely, the clause is the disjunction
     of all y_{p,w} where w is v or a neighbour of v, for all positions p.

* Edge cases are handled directly without constructing the general
  encoding:
    - k < 0 → unsatisfiable (a formula with an empty clause).
    - n = 0 → trivially satisfiable (empty formula).
    - k >= n → trivially satisfiable (empty formula) because any set of
      at most n vertices can dominate the graph.

The reduction runs in time polynomial in n, |E| and k and produces a
correct SAT instance.
"""

from typing import List, Dict, Any


def _var_id(p: int, v: int, n: int) -> int:
    """Return the SAT variable number for position ``p`` and vertex ``v``.

    Vertices are 0..n (inclusive) where ``n`` is the dummy vertex.  Positions
    are 0..k-1.  Variables are numbered starting from 1.
    """
    # (n+1) vertices per position.
    return p * (n + 1) + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Dominating Set instance to a SAT instance.

    The returned instance follows the format described in the module doc‑
    string above.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases -----------------------------------------------------------
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 0:
        # Empty graph is always dominated.
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        # Always possible to dominate with at most n vertices.
        return {"num_vars": 0, "clauses": []}

    # Build adjacency list.
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        # Undirected edge.
        if 0 <= u < n and 0 <= v < n and u != v:
            adj[u].append(v)
            adj[v].append(u)

    clauses: List[List[int]] = []
    num_vars = k * (n + 1)  # include dummy vertex.

    # 1. At least one vertex (including dummy) per position.
    for p in range(k):
        clause = [_var_id(p, v, n) for v in range(n + 1)]
        clauses.append(clause)

        # 2. No two different vertices in the same position.
        for v in range(n + 1):
            for w in range(v + 1, n + 1):
                clauses.append([-_var_id(p, v, n), -_var_id(p, w, n)])

    # 3. A real vertex cannot be selected in two different positions.
    for v in range(n):  # real vertices only
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-_var_id(p, v, n), -_var_id(q, v, n)])

    # 4. Domination clauses.
    for v in range(n):
        literals: List[int] = []
        # v itself
        for p in range(k):
            literals.append(_var_id(p, v, n))
        # neighbours
        for u in adj[v]:
            for p in range(k):
                literals.append(_var_id(p, u, n))
        # The clause must be non‑empty (graph may have isolated vertices,
        # in which case literals are just the selections of v).
        clauses.append(literals)

    return {"num_vars": num_vars, "clauses": clauses}

