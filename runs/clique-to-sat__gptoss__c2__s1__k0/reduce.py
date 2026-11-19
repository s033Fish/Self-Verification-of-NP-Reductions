"""Clique to SAT reduction.

The source problem is *Clique* with instances of the form
```
{"n": n, "edges": [[u, v], ...], "k": k}
```
where vertices are numbered ``0..n-1`` and ``edges`` contains each undirected
edge exactly once.

The target problem is *SAT* in conjunctive normal form with instances of the
form
```
{"num_vars": m, "clauses": [[literal, ...], ...]}
```
where a *literal* is a signed integer: ``+v`` means variable ``v`` is true,
``-v`` means it is false.

The reduction follows the classic polynomial‑time construction used in textbook
proofs that Clique ≤<sub>p</sub> SAT.  For a given graph ``G`` and integer ``k`` we
create boolean variables ``x_{i,p}`` (``i`` vertex, ``p`` position in the
potential clique).  Variable ``x_{i,p}`` is true iff vertex ``i`` occupies the
``p``‑th position of a size‑``k`` clique.

Constraints encoded as clauses:
1. **Each position is occupied** – for every position ``p`` there must be at
   least one vertex: ``(x_{0,p} ∨ x_{1,p} ∨ … ∨ x_{n-1,p})``.
2. **At most one vertex per position** – for every position ``p`` and every pair
   of distinct vertices ``i < j``: ``(¬x_{i,p} ∨ ¬x_{j,p})``.
3. **A vertex appears at most once** – for every vertex ``i`` and every pair of
   distinct positions ``p < q``: ``(¬x_{i,p} ∨ ¬x_{i,q})``.
4. **Non‑edges are forbidden** – if ``(i, j)`` is *not* an edge, the two
   vertices cannot both be in the clique at the same position: for each
   position ``p`` add ``(¬x_{i,p} ∨ ¬x_{j,p})``.

Variable numbering (required by the SAT format) is a simple bijection:
``var_id(i, p) = i * k + p + 1`` where ``i`` ∈ ``[0, n)`` and ``p`` ∈ ``[0, k)``.
Thus we have ``m = n * k`` variables.

Edge‑case handling aligns the SAT instance with the semantics of Clique:
* ``k <= 0`` – Clique is always a YES instance.  We return a trivially
  satisfiable formula: zero variables and zero clauses.
* ``k = 1`` – The construction naturally yields a formula that is satisfiable
  iff the graph has at least one vertex, matching the Clique definition.
* ``k > n`` – The generated formula is unsatisfiable because the clauses from
  (1) cannot be simultaneously satisfied with the at‑most‑once constraints.

The implementation runs in polynomial time: building the edge set takes
``O(m)`` where ``m`` is the number of edges, and the total number of generated
clauses is ``O(k·n²)`` which is polynomial in the size of the input.
"""

from typing import List, Dict, Any, Set, Tuple


def _var_id(i: int, p: int, k: int) -> int:
    """Return the SAT variable number for vertex *i* in position *p*.

    Variables are numbered from 1 upwards as required by the SAT format.
    """
    return i * k + p + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent SAT instance.

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

    # Edge cases that can be handled directly.
    if k <= 0:
        # Always YES – return a trivially satisfiable formula.
        return {"num_vars": 0, "clauses": []}

    # Build a set of undirected edges for O(1) lookup.
    edge_set: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Number of variables.
    num_vars = n * k
    clauses: List[List[int]] = []

    # 1. Each position must be occupied by at least one vertex.
    for p in range(k):
        clause = [_var_id(i, p, k) for i in range(n)]
        # If n == 0 this clause will be empty, which correctly makes the
        # formula unsatisfiable (matching the Clique definition for k>0).
        clauses.append(clause)

    # 2. At most one vertex per position.
    for p in range(k):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-_var_id(i, p, k), -_var_id(j, p, k)])

    # 3. Each vertex appears in at most one position.
    for i in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-_var_id(i, p, k), -_var_id(i, q, k)])

    # 4. Non‑edges cannot both be chosen in the same position.
    # Iterate over all unordered pairs of vertices that are NOT edges.
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in edge_set:
                for p in range(k):
                    clauses.append([-_var_id(i, p, k), -_var_id(j, p, k)])

    return {"num_vars": num_vars, "clauses": clauses}

