"""Reduction from SAT to Independent Set.

The reduction follows the classic textbook construction:

* For each clause *C_i* of the SAT formula we create a vertex for every
  literal occurring in that clause.  Vertices belonging to the same clause
  form a clique – they are all mutually adjacent.  This forces any
  independent set to pick **at most** one vertex from each clause.

* For any two vertices that correspond to complementary literals (e.g.
  ``x`` and ``-x``) we add an edge, regardless of whether they belong to the
  same clause or different clauses.  This guarantees that an independent set
  cannot contain both a variable and its negation.

If the original CNF formula is satisfiable, we can select, for each clause,
one true literal; the corresponding vertices are pair‑wise non‑adjacent, so
they form an independent set of size *k* where *k* is the number of clauses.
Conversely, an independent set of size at least *k* must contain exactly one
vertex from each clause and cannot contain complementary literals, which
directly yields a satisfying assignment.

Edge cases are handled explicitly:

* An empty list of clauses is trivially satisfiable.  The reduction returns
  a graph with ``n = 0`` vertices and ``k = 0`` – the Independent Set problem
  answers *yes* because ``k <= 0``.
* A clause that is the empty list ``[]`` can never be satisfied.  The
  reduction still counts that clause toward ``k`` but creates no vertices for
  it, making it impossible to achieve an independent set of size ``k``.

The implementation runs in time polynomial in the size of the input
instance (linear in the number of literal occurrences).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Sat, IndependentSet

def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a SAT formula as defined in ``Sat``.

    Returns
    -------
    dict
        An Independent Set instance (dictionary) satisfying the contract of
        ``IndependentSet`` where the answer is *yes* iff the original SAT
        instance is satisfiable.
    """
    # Validate the input using the provided helper – this will raise if the
    # instance is malformed, matching the expectations of the task.
    Sat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # ``vertex_info`` maps a vertex index to a tuple (var, sign) where sign is
    # +1 for a positive literal and -1 for a negative literal.
    vertex_info: List[Tuple[int, int]] = []
    # For each clause we store the list of vertex indices belonging to it.
    clause_vertices: List[List[int]] = []

    for clause in clauses:
        current_clause_vertices: List[int] = []
        for lit in clause:
            var = abs(lit)
            sign = 1 if lit > 0 else -1
            vertex_idx = len(vertex_info)
            vertex_info.append((var, sign))
            current_clause_vertices.append(vertex_idx)
        clause_vertices.append(current_clause_vertices)

    n = len(vertex_info)
    edges_set = set()

    # 1. Add edges inside each clause (clique).
    for verts in clause_vertices:
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                u, v = verts[i], verts[j]
                if u != v:
                    edges_set.add((min(u, v), max(u, v)))

    # 2. Add edges between complementary literals.
    #   We iterate over all pairs of vertices (i < j) and add an edge if they
    #   refer to the same variable with opposite signs.
    for i in range(n):
        var_i, sign_i = vertex_info[i]
        for j in range(i + 1, n):
            var_j, sign_j = vertex_info[j]
            if var_i == var_j and sign_i != sign_j:
                edges_set.add((i, j))

    edges = [[u, v] for (u, v) in sorted(edges_set)]
    k = len(clauses)  # we need at least one vertex per clause

    result: Dict = {"n": n, "edges": edges, "k": k}
    # Validate the produced instance.
    IndependentSet.validate(result)
    return result

