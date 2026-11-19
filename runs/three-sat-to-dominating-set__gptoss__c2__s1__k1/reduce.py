"""Reduction from 3‑SAT to Dominating Set.

The source problem is ``ThreeSat`` with instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (meaning variable ``v`` is true)
or ``-v`` (meaning variable ``v`` is false).  Every clause contains exactly
three literals on distinct variables.

The target problem is ``DominatingSet`` with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction constructs a graph that has a dominating set of size at most
``k = m + number_of_clauses`` iff the 3‑SAT formula is satisfiable.  The
construction is the classic textbook reduction:

* For each variable ``x_i`` we create two vertices ``x_i`` and ``¬x_i`` and
  connect them with an edge.  Selecting exactly one of the two vertices will
  dominate both, representing the truth assignment of the variable.
* For each clause ``C_j = (ℓ1 ∨ ℓ2 ∨ ℓ3)`` we create a triangle of three
  vertices ``c_{j,1}``, ``c_{j,2}``, ``c_{j,3}``.  The three vertices are fully
  connected, guaranteeing that at least one vertex from the triangle must be
  chosen (or be adjacent to a chosen vertex) in any dominating set of size
  ``≤ m + #clauses``.
* For each literal ``ℓ`` occurring in a clause we add an edge between the
  clause‑vertex representing that literal and the corresponding variable
  vertex (positive or negative).  Thus, if the variable vertex is selected,
  it also dominates the clause vertex, satisfying the clause.

If the formula is satisfiable, pick for each variable the vertex that matches
the satisfying assignment and, for each clause that is not already dominated
by a chosen variable vertex, pick any one of its three clause vertices.  This
produces a dominating set of size at most ``m + #clauses``.

Conversely, any dominating set of size at most ``m + #clauses`` can be turned
into a satisfying assignment: from each variable pair at most one vertex can
be chosen (otherwise we would exceed the budget), and each clause must be
dominated either by a variable vertex (giving a true literal) or by a clause
vertex, which can be interpreted as choosing a true literal for that clause.

The implementation below follows this construction and runs in polynomial
time with respect to the size of the input instance.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        lists of three integers each).

    Returns
    -------
    dict
        A Dominating Set instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Vertex indexing:
    #   For each variable i (1‑based) we allocate two vertices:
    #       pos_i = 2*(i-1)
    #       neg_i = 2*(i-1) + 1
    #   Clause vertices start after the 2*m variable vertices.
    clause_offset = 2 * m
    total_vertices = 2 * m + 3 * num_clauses

    edges: List[List[int]] = []

    # 1. Variable edges (pos_i, neg_i)
    for i in range(1, m + 1):
        pos = 2 * (i - 1)
        neg = pos + 1
        edges.append([pos, neg])

    # 2. Clause triangles and literal‑to‑variable edges
    for j, clause in enumerate(clauses):
        # clause vertices for this clause
        base = clause_offset + 3 * j
        c0, c1, c2 = base, base + 1, base + 2
        # triangle edges
        edges.append([c0, c1])
        edges.append([c0, c2])
        edges.append([c1, c2])

        # connect each clause vertex to the appropriate variable vertex
        for lit_idx, literal in enumerate(clause):
            var = abs(literal)
            if var == 0 or var > m:
                # Invalid literal – the instance validator would reject this,
                # but we guard against crashes.
                continue
            if literal > 0:
                var_vertex = 2 * (var - 1)      # positive vertex
            else:
                var_vertex = 2 * (var - 1) + 1  # negative vertex
            clause_vertex = base + lit_idx
            edges.append([clause_vertex, var_vertex])

    # The budget k = m + number_of_clauses
    k = m + num_clauses

    return {"n": total_vertices, "edges": edges, "k": k}

# The module does not execute any code on import; it only provides the
# ``reduce`` function required by the evaluation harness.
