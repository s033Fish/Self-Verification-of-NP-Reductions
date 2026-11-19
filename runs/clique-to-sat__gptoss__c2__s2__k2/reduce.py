"""Reduction from Clique to SAT.

The source problem (Clique) is defined as:
    instance = {"n": n, "edges": [[u, v], ...], "k": k}
    Vertices are 0..n-1.  An undirected edge is given once as [u, v] with u != v.
    The question is whether the graph contains a clique of size at least k.

The target problem (Sat) expects instances of the form:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
    Literals are integers: a positive integer v denotes the variable v is true,
    a negative integer -v denotes the variable v is false.

We implement the classic polynomial‑time reduction that creates a Boolean
variable x_{i,v} meaning "vertex v occupies the i‑th position of the clique"
where i ranges from 0 to k-1 and v ranges from 0 to n-1.  The reduction
produces the following constraints as CNF clauses:

1. **Every position is occupied** – for each i we add a clause that at least
   one vertex is chosen for that position.
2. **A vertex cannot appear in two positions** – for each vertex v and each
   pair of distinct positions i < j we add a clause (¬x_{i,v} ∨ ¬x_{j,v}).
3. **Non‑edges are forbidden** – for any pair of vertices (u, v) that is NOT
   an edge, and for any two distinct positions i != j, we add a clause
   (¬x_{i,u} ∨ ¬x_{j,v}).  This prevents the selection of two non‑adjacent
   vertices in the clique.

Edge cases are handled explicitly so that the reduction always produces a
correct SAT instance:

* k <= 0 – always a YES instance; we output an empty formula (no clauses),
  which is trivially satisfiable.
* k == 1 – also always YES when n >= 1; again we output the empty formula.
* k > n – always NO; we output a formula containing a single empty clause
  ("[]"), which is unsatisfiable.

The function ``reduce(instance)`` follows the specification required by the
testing harness: it receives a Clique instance and returns a SAT instance.
It runs in time polynomial in n and k.
"""

from typing import List, Dict, Set, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n", "edges", and "k" as described above.

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Handle trivial edge cases directly.
    if k <= 0:
        # Empty formula is always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        # Satisfiable iff there is at least one vertex.  If n == 0 then k>n
        # (handled below).  For n >= 1 we can again return an empty formula.
        if n >= 1:
            return {"num_vars": 0, "clauses": []}
        # else fall through to the k > n case.
    if k > n:
        # Unsatisfiable: produce a formula with a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency set for O(1) edge queries.
    edge_set: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Helper to map (position i, vertex v) to a SAT variable number (1‑based).
    def var(i: int, v: int) -> int:
        return i * n + v + 1  # +1 because SAT variables start at 1

    clauses: List[List[int]] = []

    # 1. Each position i must contain at least one vertex.
    for i in range(k):
        clause = [var(i, v) for v in range(n)]
        clauses.append(clause)

    # 2. No vertex appears in two different positions.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var(i, v), -var(j, v)])

    # 3. Non‑edges cannot both be selected.
    # Pre‑compute all unordered non‑edge pairs (u, v) with u != v.
    non_edges: List[Tuple[int, int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                non_edges.append((u, v))

    # For each ordered pair of distinct positions i != j, forbid picking a
    # non‑edge pair.
    for i in range(k):
        for j in range(k):
            if i == j:
                continue
            for u, v in non_edges:
                # (¬x_{i,u} ∨ ¬x_{j,v})
                clauses.append([-var(i, u), -var(j, v)])
                # Also forbid the opposite ordering (¬x_{i,v} ∨ ¬x_{j,u})
                clauses.append([-var(i, v), -var(j, u)])

    num_vars = k * n
    return {"num_vars": num_vars, "clauses": clauses}

# The module may be imported by the testing harness; no top‑level code is
# executed.
