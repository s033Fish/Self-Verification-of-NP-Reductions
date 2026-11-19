"""Reduction from 3-SAT to Independent Set.

The source problem (ThreeSat) is defined as a dictionary:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer.  A positive integer ``v`` denotes
the literal ``x_v`` (variable *v* set to true) and a negative integer ``-v``
denotes ``¬x_v``.  Every clause contains exactly three literals on distinct
variables.

The target problem (IndependentSet) expects a dictionary:

    {"n": n, "edges": [[u, v], ...], "k": k}

Vertices are numbered ``0 .. n-1`` and ``edges`` is a list of unordered
pairs.  The instance is a *yes* instance iff the graph contains an
independent set of size at least ``k``.

Standard reduction:

* For each clause we create a triangle of three vertices – one for each
  literal.  Selecting more than one vertex from the same clause would then
  violate independence, so any independent set can contain at most one
  vertex per clause.
* For any two vertices that correspond to complementary literals (e.g.
  ``x`` and ``¬x``) we add an edge.  This prevents the independent set from
  picking both, enforcing consistency of the assignment.
* We set ``k`` equal to the number of clauses.  Therefore an independent set
  of size ``k`` must pick exactly one vertex from each clause, and the set of
  chosen literals yields a satisfying assignment.

The construction runs in polynomial time (quadratic in the number of
clauses, which is fine for the intended use).
"""

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        An Independent Set instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Each clause contributes three vertices.
    n = 3 * num_clauses
    k = num_clauses

    edges_set: Set[Tuple[int, int]] = set()

    # Helper to add an undirected edge without duplicates.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges_set.add((u, v))

    # Map each vertex to its literal for quick lookup when adding complement edges.
    vertex_literal: List[int] = []  # index is vertex id, value is literal

    for ci, clause in enumerate(clauses):
        # clause should have exactly three literals according to the spec
        # but we tolerate any length gracefully.
        base = ci * 3
        for offset, lit in enumerate(clause[:3]):
            v_id = base + offset
            vertex_literal.append(lit)
        # If fewer than three literals (should not happen), pad with dummy literals
        for offset in range(len(clause), 3):
            v_id = base + offset
            vertex_literal.append(0)  # 0 will never match a complement

        # Add edges to form a triangle within the clause.
        a, b, c = base, base + 1, base + 2
        add_edge(a, b)
        add_edge(a, c)
        add_edge(b, c)

    # Add edges between complementary literals from different clauses.
    for u in range(n):
        lit_u = vertex_literal[u]
        if lit_u == 0:
            continue
        for v in range(u + 1, n):
            lit_v = vertex_literal[v]
            if lit_v == 0:
                continue
            # If literals are complements (e.g., 5 and -5)
            if lit_u == -lit_v:
                # Ensure they are not from the same clause – those are already
                # connected via the triangle, but adding the edge again is harmless.
                add_edge(u, v)

    edges = [[u, v] for (u, v) in sorted(edges_set)]

    return {"n": n, "edges": edges, "k": k}

