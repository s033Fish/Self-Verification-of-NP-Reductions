"""Reduction from Vertex Cover to SAT.

The source problem is defined in ``problems.py`` as ``VertexCover`` with
instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The target problem is ``Sat`` with instance format:

    {"num_vars": m, "clauses": [[literal, ...], ...]}

The reduction creates a CNF formula that is satisfiable iff the input
graph has a vertex cover of size *at most* ``k``.

Encoding strategy
------------------
We introduce Boolean variables ``y_{i,v}`` meaning *the i‑th selected
vertex (0 ≤ i < k) is vertex v* and auxiliary variables ``e_i`` meaning
*the i‑th slot is empty*.  This allows us to encode a cover of size ≤ k –
unused slots are marked by ``e_i``.

Variable indexing (1‑based as required by the SAT format):
    var_id(i, v) = i * n + v + 1          for 0 ≤ i < k, 0 ≤ v < n
    var_id_e(i)   = k * n + i + 1        for 0 ≤ i < k

Constraints encoded as clauses (all in CNF):
1. **Each slot chooses exactly one option** (a vertex or empty):
   - At least one:   e_i ∨ y_{i,0} ∨ … ∨ y_{i,n‑1}
   - At most one:   for every pair (a,b) among {e_i} ∪ {y_{i,v}}
     add (¬a ∨ ¬b).
2. **A vertex cannot be chosen in two different slots** (ensuring at most
   k distinct vertices): for each vertex v and each i < j, add
   (¬y_{i,v} ∨ ¬y_{j,v}).
3. **Edge coverage**: for each edge (u, v) there must be a slot that
   selects u or v:
   (y_{0,u} ∨ … ∨ y_{k‑1,u} ∨ y_{0,v} ∨ … ∨ y_{k‑1,v})

Edge cases
~~~~~~~~~~
* ``k < 0`` – always a NO instance.  We return an unsatisfiable formula
  consisting of a single empty clause.
* ``k == 0`` – the formula is satisfiable iff the graph has no edges.
  If there is any edge we again return an unsatisfiable formula with an
  empty clause; otherwise we return a trivially satisfiable formula with
  zero variables and no clauses.

The construction uses O(k·n + k²·n + m·k) clauses and O(k·n) variables,
which is polynomial in the size of the input.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a SAT instance.

    Parameters
    ----------
    instance: dict with keys ``n``, ``edges`` and ``k`` as described above.

    Returns
    -------
    dict: a SAT instance in the required format.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Helper to create an unsatisfiable formula (single empty clause).
    def unsat() -> Dict[str, Any]:
        return {"num_vars": 0, "clauses": [[]]}

    # k < 0 : always NO.
    if k < 0:
        return unsat()

    # k == 0 : only YES when there are no edges.
    if k == 0:
        if edges:
            return unsat()
        else:
            return {"num_vars": 0, "clauses": []}

    # General case k > 0.
    num_vars = k * n + k  # y variables + e variables
    clauses: List[List[int]] = []

    # Mapping functions for variable IDs (1‑based).
    def var_y(i: int, v: int) -> int:
        return i * n + v + 1

    def var_e(i: int) -> int:
        return k * n + i + 1

    # 1. Each slot selects at least one option (empty or a vertex).
    for i in range(k):
        clause = [var_e(i)] + [var_y(i, v) for v in range(n)]
        clauses.append(clause)

    # 1b. At most one option per slot.
    for i in range(k):
        # List of all literals for this slot.
        literals = [var_e(i)] + [var_y(i, v) for v in range(n)]
        # Add pairwise negative clauses.
        for a_idx in range(len(literals)):
            for b_idx in range(a_idx + 1, len(literals)):
                clauses.append([-literals[a_idx], -literals[b_idx]])

    # 2. A vertex cannot appear in two different slots.
    for v in range(n):
        for i in range(k):
            for j in range(i + 1, k):
                clauses.append([-var_y(i, v), -var_y(j, v)])

    # 3. Edge coverage clauses.
    for (u, v) in edges:
        clause = []
        for i in range(k):
            clause.append(var_y(i, u))
            clause.append(var_y(i, v))
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

