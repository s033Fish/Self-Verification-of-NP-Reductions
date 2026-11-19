"""Clique to SAT reduction.

The source problem is **Clique** with instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are numbered 0..n-1.

The target problem is **Sat** (CNF) with instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are signed integers: +v means variable v is true, -v means false.

We implement the classic polynomial‑time reduction that introduces a Boolean
variable `x_{i,v}` meaning *vertex v occupies position i in the alleged
clique* (positions are 0 … k‑1).  The reduction produces a CNF formula that is
 satisfiable iff the original graph contains a clique of size **at least** k.

The encoding uses three families of clauses:

1. **Each position is occupied by at least one vertex** – a single clause per
   position containing all variables for that position.
2. **A vertex cannot occupy two different positions** – for every vertex v
   and every pair of distinct positions i < j we add the clause
   (¬x_{i,v} ∨ ¬x_{j,v}).
3. **Non‑edges cannot both be selected** – for every unordered non‑edge {u, v}
   (including u == v is irrelevant because clause 2 already forbids a vertex
   appearing twice) and for every ordered pair of positions i < j we add the
   two clauses (¬x_{i,u} ∨ ¬x_{j,v}) and (¬x_{i,v} ∨ ¬x_{j,u}).  These clauses
   ensure that any two chosen vertices are adjacent.

Edge‑case handling follows the specification of the source problem:

* k <= 0 – always a *yes* instance.  We output an empty CNF (no clauses), which
  is trivially satisfiable.
* k == 1 – also always *yes* when n >= 1.  Again an empty CNF suffices.
* k > n – always *no*.  We output a formula containing a single empty clause
  `[]`, which is unsatisfiable.

The construction runs in time O(k^2 * n^2) which is polynomial in the input
size.
"""

from typing import List, Dict, Tuple, Set


def _var_index(i: int, v: int, n: int) -> int:
    """Return the SAT variable number for position i and vertex v.

    Variables are numbered starting from 1 as required by the SAT format.
    The total number of variables is k * n.
    """
    return i * n + v + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary following the Clique specification.

    Returns
    -------
    dict
        A SAT instance dictionary.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling ----------------------------------------------------
    if k <= 0:
        # Empty formula – always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        # Also always satisfiable when there is at least one vertex.
        return {"num_vars": 0, "clauses": []}
    if k > n:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency set for quick lookup.
    adj: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        adj.add((u, v))

    # Helper to test whether (u, v) is an edge (undirected).
    def is_edge(u: int, v: int) -> bool:
        if u == v:
            return False
        if u > v:
            u, v = v, u
        return (u, v) in adj

    clauses: List[List[int]] = []

    # 1. Each position i must have at least one vertex.
    for i in range(k):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 2. No vertex appears in two positions.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Non‑edges cannot both be selected.
    # Enumerate all unordered non‑edges.
    non_edges: List[Tuple[int, int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if not is_edge(u, v):
                non_edges.append((u, v))

    for (u, v) in non_edges:
        for i in range(k):
            for j in range(i + 1, k):
                # (¬x_{i,u} ∨ ¬x_{j,v})
                clauses.append([-_var_index(i, u, n), -_var_index(j, v, n)])
                # (¬x_{i,v} ∨ ¬x_{j,u})
                clauses.append([-_var_index(i, v, n), -_var_index(j, u, n)])

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}

