"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) instance format is:
    {"n": int, "edges": [[u, v], ...], "k": int}
where vertices are 0..n-1 and edges are undirected.

The target problem (Sat) instance format is:
    {"num_vars": int, "clauses": [[literal, ...], ...]}
Literals are represented as signed integers: a positive integer +v means
variable v is true, a negative integer -v means variable v is false.

We construct a polynomial‑time many‑one reduction.  For each vertex *i*
we introduce a Boolean variable ``a_i`` (selected in the dominating set).
To enforce the cardinality bound ``|D| <= k`` we introduce auxiliary
variables ``b_{j,i}`` meaning *vertex i* occupies *slot j* (1 ≤ j ≤ k).
The constraints are encoded as CNF clauses:

1. **Domination** – for every vertex v, at least one of ``a_v`` or one of
   its neighbours must be true.
2. **Link selection to a slot** – if ``a_i`` is true then it must occupy
   some slot: ``¬a_i ∨ b_{1,i} ∨ … ∨ b_{k,i}``.
3. **At most one vertex per slot** – for each slot j and distinct vertices
   i ≠ i', ``¬b_{j,i} ∨ ¬b_{j,i'}``.

These clauses guarantee that any satisfying assignment corresponds to a
dominating set of size ≤ k, and vice‑versa.  The construction uses
``n + k·n`` variables and O(n·k + n·deg + k·n²) clauses, which is polynomial
in the input size.

Edge cases:
* ``k < 0`` – the source instance is always a NO instance, so we return an
  unsatisfiable SAT formula (a single empty clause).
* ``n = 0`` – no vertices, the domination constraints are vacuous; the
  resulting SAT instance has no clauses and is trivially satisfiable, which
  matches the source answer.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Dominating Set instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
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

    # If k is negative the source answer is always NO.  Produce an
    # unsatisfiable SAT formula: a single empty clause.
    if k < 0:
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency list.
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        # The input guarantees u != v and that each undirected edge appears
        # only once.
        adj[u].append(v)
        adj[v].append(u)

    # Variable indexing:
    #   a_i  (vertex i selected)          ->  i + 1               (1‑based)
    #   b_{j,i} (vertex i occupies slot j) -> n + (j‑1)*n + i + 1
    # Total number of variables = n + k * n.
    num_vars = n + k * n
    clauses: List[List[int]] = []

    # 1. Domination clauses: for each vertex v, (a_v ∨ a_u1 ∨ a_u2 ∨ ...).
    for v in range(n):
        clause: List[int] = [v + 1]  # a_v (positive literal)
        for u in adj[v]:
            clause.append(u + 1)  # a_u
        clauses.append(clause)

    # 2. Link each selected vertex to at least one slot.
    #    Clause: (¬a_i ∨ b_{1,i} ∨ b_{2,i} ∨ ... ∨ b_{k,i})
    for i in range(n):
        clause: List[int] = [-(i + 1)]  # ¬a_i
        for j in range(1, k + 1):
            b_idx = n + (j - 1) * n + i + 1
            clause.append(b_idx)
        clauses.append(clause)

    # 3. At most one vertex per slot: for each slot j and each pair i < i',
    #    (¬b_{j,i} ∨ ¬b_{j,i'}).
    for j in range(1, k + 1):
        base = n + (j - 1) * n  # first b variable index for this slot (0‑based offset)
        for i1 in range(n):
            b1 = base + i1 + 1
            for i2 in range(i1 + 1, n):
                b2 = base + i2 + 1
                clauses.append([-b1, -b2])

    return {"num_vars": num_vars, "clauses": clauses}

