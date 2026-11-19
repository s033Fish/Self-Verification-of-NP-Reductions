"""Reduction from Vertex Cover to SAT.

The source problem (VertexCover) instance format is a dictionary:
    {"n": int, "edges": [[u, v], ...], "k": int}
where vertices are numbered 0..n-1.

The target problem (Sat) instance format is a dictionary:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are represented as signed integers: +v for variable v (true)
and -v for variable v (false). Variable indices start at 1.

We construct a SAT formula that is satisfiable iff the given graph has a
vertex cover of size at most ``k``.

Encoding strategy
-------------------
We introduce a Boolean variable ``y_{i,v}`` meaning "vertex *v* occupies
position *i* in the cover" where ``i`` ranges from 0 to ``k-1`` and ``v``
from 0 to ``n-1``.  The total number of variables is ``k * n``.

Constraints added:
1. **Edge coverage** – for each edge (u, v) we need at least one of its
   endpoints selected in some position:
   ``(y_{0,u} ∨ … ∨ y_{k-1,u} ∨ y_{0,v} ∨ … ∨ y_{k-1,v})``.
2. **Exactly one vertex per position** – each position must contain at
   least one vertex and at most one vertex.  The "at least one" clause is
   ``(y_{i,0} ∨ y_{i,1} ∨ … ∨ y_{i,n-1})``.  The "at most one" clauses are
   pairwise negative clauses ``(¬y_{i,a} ∨ ¬y_{i,b})`` for all ``a < b``.
3. **A vertex cannot appear in two positions** – for each vertex ``v``
   and each pair of distinct positions ``i < j`` we add ``(¬y_{i,v} ∨ ¬y_{j,v})``.

If a vertex cover of size ≤ k exists, we can extend it to exactly k by
adding arbitrary additional vertices, so the formula is satisfiable iff a
cover of size ≤ k exists.

Special cases handled explicitly:
* ``k < 0`` – always a NO instance.  We output an unsatisfiable formula
  consisting of a single empty clause.
* ``k >= n`` – always a YES instance.  We output a trivially satisfiable
  formula with no clauses.

The reduction runs in time polynomial in ``n``, ``|E|`` and ``k``.
"""

from typing import List, Dict


def _var_index(i: int, v: int, n: int) -> int:
    """Map position *i* and vertex *v* to a SAT variable number (1‑based).

    Variables are numbered consecutively: first all vertices for position
    0, then for position 1, and so on.
    """
    return i * n + v + 1  # +1 because SAT variables start at 1


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to an equivalent SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A SAT instance dictionary with keys ``"num_vars"`` and ``"clauses"``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases ------------------------------------------------------------
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if k >= n:
        # Trivially satisfiable (no constraints needed).
        return {"num_vars": 0, "clauses": []}

    # General case ----------------------------------------------------------
    num_vars = k * n
    clauses: List[List[int]] = []

    # 1. Edge coverage constraints
    for u, v in edges:
        clause: List[int] = []
        for i in range(k):
            clause.append(_var_index(i, u, n))
            clause.append(_var_index(i, v, n))
        clauses.append(clause)

    # 2. At least one vertex per position
    for i in range(k):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 3. At most one vertex per position (pairwise negative clauses)
    for i in range(k):
        for a in range(n):
            var_a = _var_index(i, a, n)
            for b in range(a + 1, n):
                var_b = _var_index(i, b, n)
                clauses.append([-var_a, -var_b])

    # 4. A vertex cannot occupy two different positions
    for v in range(n):
        for i in range(k):
            var_i = _var_index(i, v, n)
            for j in range(i + 1, k):
                var_j = _var_index(j, v, n)
                clauses.append([-var_i, -var_j])

    return {"num_vars": num_vars, "clauses": clauses}

