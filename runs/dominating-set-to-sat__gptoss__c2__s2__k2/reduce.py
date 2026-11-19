"""Reduction from Dominating Set to SAT.

The source problem (DominatingSet) instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem (Sat) instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}

We construct a SAT formula that is satisfiable iff the given graph has a
 dominating set of size at most *k*.

Reduction idea
---------------
We introduce boolean variables a_{i,p} (encoded as a single SAT variable) that
mean "vertex *i* is chosen for position *p* in the dominating set" where
*p* ranges from 0 to k‑1.  Positions allow us to bound the size of the set to
*k*: a vertex may appear in several positions, which effectively lets us pad
the set with duplicates when the actual dominating set is smaller than *k*.

Constraints encoded as clauses:
1. **Each position chooses exactly one vertex** – at least one (a clause with
   all a_{i,p}) and at most one (pairwise negative clauses).
2. **Dominating condition** – for every vertex *v* there must be a position
   *p* such that the vertex selected at *p* is either *v* itself or a neighbor
   of *v*.  This yields a clause that is the disjunction of all a_{i,p} that
   dominate *v*.

Edge‑case handling follows the specification of Dominating Set:
* k < 0 → unsatisfiable (empty clause).
* n = 0 → trivially satisfiable (no clauses, zero variables).
* k >= n → trivially satisfiable (we can select all vertices, so we return an
  empty formula).

The construction uses O(n·k) variables and O(n²·k) clauses, which is
polynomial in the size of the input.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Dominating Set instance to an equivalent SAT instance.

    Parameters
    ----------
    instance: dict
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

    # Edge cases handled directly according to the source specification.
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}
    if n == 0:
        # Empty graph is always dominated.
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        # When k is large enough we can always dominate by taking all vertices.
        # Return a trivially satisfiable formula.
        return {"num_vars": 0, "clauses": []}
    if k == 0:
        # Non‑empty graph cannot be dominated by an empty set.
        return {"num_vars": 1, "clauses": [[]]}

    # Build adjacency sets for quick lookup.
    adj: List[set] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Mapping (vertex, position) -> SAT variable number (1‑based).
    var_index = {}
    cur = 1
    for i in range(n):
        for p in range(k):
            var_index[(i, p)] = cur
            cur += 1
    num_vars = cur - 1
    clauses: List[List[int]] = []

    # 1. Each position must choose at least one vertex.
    for p in range(k):
        clause = [var_index[(i, p)] for i in range(n)]
        clauses.append(clause)

    # 2. Each position chooses at most one vertex (pairwise negative clauses).
    for p in range(k):
        for i in range(n):
            vi = var_index[(i, p)]
            for j in range(i + 1, n):
                vj = var_index[(j, p)]
                clauses.append([-vi, -vj])

    # 3. Dominating constraints: for every vertex v, at least one selected
    #    vertex (in any position) must dominate it.
    for v in range(n):
        lits: List[int] = []
        for p in range(k):
            for i in range(n):
                if i == v or v in adj[i]:
                    lits.append(var_index[(i, p)])
        # The list is never empty because the graph may have isolated vertices;
        # in that case only i == v contributes.
        clauses.append(lits)

    return {"num_vars": num_vars, "clauses": clauses}

