"""Reduction from 3‑SAT to Clique.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (variable *v* is true) or
``-v`` (variable *v* is false).  Every clause contains exactly three
distinct variables.

The target problem is ``Clique`` with an instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction is the classic one used in textbooks:

* For each clause we create three vertices – one for each literal.
* We connect two vertices with an edge iff they belong to *different*
  clauses and the corresponding literals are **not** contradictory
  (i.e., they do not refer to the same variable with opposite signs).
* We ask for a clique of size ``k`` equal to the number of clauses.

If the original formula is satisfiable, we can pick a true literal from
each clause; the corresponding vertices form a clique because no two of
them are contradictory.  Conversely, any clique of size ``k`` selects one
vertex from each clause, and the literals they represent can be made true
simultaneously – otherwise the clique would contain a contradictory pair
and would not be a clique.

Edge cases:
  * An empty formula (no clauses) is always satisfiable.  We output a
    Clique instance with ``k = 0`` (which is trivially a yes‑instance for
    any graph, even an empty graph).
  * The construction works for any number of variables; the value
    ``num_vars`` is irrelevant for the reduction.

The implementation below follows this description and runs in time
polynomial in the size of the 3‑SAT instance.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``num_vars`` and ``clauses`` as described
        in the problem statement.

    Returns
    -------
    dict
        A Clique instance ``{"n": n, "edges": edges, "k": k}`` such that
        the Clique instance is a yes‑instance iff the original 3‑SAT
        instance is satisfiable.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: no clauses → always satisfiable.
    if num_clauses == 0:
        # k = 0 is always a yes‑instance, even with an empty graph.
        return {"n": 0, "edges": [], "k": 0}

    # Assign a unique vertex id to each literal in each clause.
    # Vertex ids are 0 .. 3*num_clauses-1.
    n = 3 * num_clauses
    edges: List[List[int]] = []

    # Pre‑compute the vertex id for each literal for quick lookup.
    # vertex_ids[i][j] gives the id of the j‑th literal (0‑based) of clause i.
    vertex_ids: List[List[int]] = []
    for i in range(num_clauses):
        vertex_ids.append([i * 3 + j for j in range(3)])

    # Helper to test whether two literals are contradictory.
    def contradictory(lit1: int, lit2: int) -> bool:
        return abs(lit1) == abs(lit2) and (lit1 > 0) != (lit2 > 0)

    # Build edges between literals from different clauses that are not contradictory.
    for i in range(num_clauses):
        for j in range(i + 1, num_clauses):
            for idx_i, lit_i in enumerate(clauses[i]):
                for idx_j, lit_j in enumerate(clauses[j]):
                    if not contradictory(lit_i, lit_j):
                        u = vertex_ids[i][idx_i]
                        v = vertex_ids[j][idx_j]
                        edges.append([u, v])

    return {"n": n, "edges": edges, "k": num_clauses}

