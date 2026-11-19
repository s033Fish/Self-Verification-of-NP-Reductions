"""Reduction from 3‑SAT to Dominating Set.

The source problem is :class:`problems.ThreeSat` and the target problem is
``DominatingSet``.  The construction follows the classic NP‑completeness proof
for Dominating Set (see e.g. Garey & Johnson, *Computers and Intractability*).

For each variable ``x_i`` we create two vertices ``i_T`` and ``i_F`` that are
connected by an edge.  Selecting exactly one of them in a dominating set
corresponds to assigning the variable a truth value.

For each clause ``C_j = (ℓ1 ∨ ℓ2 ∨ ℓ3)`` we create a clause vertex ``c_j`` and
connect it to the three literal vertices that satisfy the clause: the true‑
vertex for a positive literal and the false‑vertex for a negative literal.

Let ``m`` be the number of variables and ``p`` the number of clauses.  The
graph therefore has ``n = 2*m + p`` vertices.  We set the budget ``k = m``.

Correctness sketch:
*If the formula is satisfiable*, choose for each variable the vertex that
represents its true literal.  These ``m`` vertices dominate the whole graph:
  - The opposite literal vertex is adjacent via the variable edge.
  - Every clause vertex is adjacent to at least one chosen literal vertex.
Hence there is a dominating set of size ``k``.

*Conversely*, any dominating set of size at most ``k = m`` must contain at
least one vertex from each variable edge (otherwise the two vertices of the
edge would be undominated).  Because there are only ``m`` vertices allowed, the
set cannot contain any clause vertices.  Therefore each clause vertex must be
 dominated by a literal vertex, which yields a satisfying assignment.

The implementation below follows this construction and returns a dictionary
compatible with the ``DominatingSet`` instance format.
"""

from __future__ import annotations

from typing import List, Dict

from problems import ThreeSat, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` specification:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.

    Returns
    -------
    dict
        A ``DominatingSet`` instance ``{"n": n, "edges": [...], "k": k}``.
    """
    # Validate input (will raise InvalidInstance if malformed).
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex numbering:
    #   For each variable i (0‑based) we create three vertices:
    #       true_i   = 3*i
    #       false_i  = 3*i + 1
    #       dummy_i  = 3*i + 2
    #   These form a triangle so that any dominating set must contain
    #   either true_i or false_i (to dominate dummy_i).
    #   Clause vertices start at 3*m.
    def true_vertex(var_idx: int) -> int:
        return 3 * var_idx

    def false_vertex(var_idx: int) -> int:
        return 3 * var_idx + 1

    def dummy_vertex(var_idx: int) -> int:
        return 3 * var_idx + 2

    edges: List[List[int]] = []

    # Build the triangle for each variable.
    for i in range(m):
        t, f, d = true_vertex(i), false_vertex(i), dummy_vertex(i)
        edges.append([t, f])
        edges.append([t, d])
        edges.append([f, d])

    # Clause vertices and connections to literals.
    for idx, clause in enumerate(clauses):
        clause_vertex = 3 * m + idx
        for lit in clause:
            var = abs(lit) - 1  # 0‑based variable index
            if lit > 0:
                lit_vertex = true_vertex(var)
            else:
                lit_vertex = false_vertex(var)
            # Add edge between clause vertex and the corresponding literal.
            u, v = (clause_vertex, lit_vertex) if clause_vertex < lit_vertex else (lit_vertex, clause_vertex)
            edges.append([u, v])

    n = 3 * m + len(clauses)
    k = m

    return {"n": n, "edges": edges, "k": k}

