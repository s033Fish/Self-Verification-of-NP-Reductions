"""Reduction from 3-SAT to Independent Set.

The source problem (ThreeSat) is given as a dictionary with keys:

* ``num_vars`` – the number of variables (unused by the reduction).
* ``clauses`` – a list of clauses, each clause being a list of three
  literals.  A literal is an integer ``v`` (positive) meaning the variable
  ``v`` is true, or ``-v`` (negative) meaning the variable ``v`` is false.

The target problem (IndependentSet) expects a dictionary with keys:

* ``n`` – number of vertices (0‑indexed).
* ``edges`` – list of undirected edges ``[u, v]`` with ``u < v``.
* ``k`` – the size of the independent set we are asking for.

The classic polynomial‑time reduction builds a triangle for each clause and
connects vertices that represent complementary literals (e.g. ``x`` and
``¬x``) across different clauses.  An independent set of size equal to the
number of clauses corresponds to picking exactly one literal from each
clause without picking a pair of complementary literals, which is exactly a
truth assignment satisfying the formula.

The implementation follows this construction:

* For each clause ``i`` (0‑based) and each of its three literals ``j`` we
  create a vertex ``v = i * 3 + j``.
* Inside each clause we add the three edges of a triangle.
* For every pair of vertices belonging to different clauses we add an edge
  when the corresponding literals are complementary – i.e. they refer to
  the same variable with opposite signs.
* ``k`` is set to the number of clauses.

The function runs in ``O(c^2)`` time where ``c`` is the number of clauses,
which is polynomial in the size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary following the ``ThreeSat`` format described above.

    Returns
    -------
    dict
        An ``IndependentSet`` instance.  The answer to the returned instance
        is *yes* iff the original 3‑SAT instance is satisfiable.
    """

    # Extract clauses; the number of variables is not needed for the
    # construction, but we keep the key for completeness.
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Vertex id for literal (clause i, position j) is i*3 + j.
    n_vertices = num_clauses * 3
    edges: List[List[int]] = []

    # Helper to add an undirected edge ensuring u < v and no duplicates.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.append([u, v])

    # 1. Add triangle edges inside each clause.
    for i in range(num_clauses):
        base = i * 3
        # three vertices: base, base+1, base+2
        add_edge(base, base + 1)
        add_edge(base, base + 2)
        add_edge(base + 1, base + 2)

    # 2. Add conflict edges between complementary literals of different clauses.
    # Build a list mapping vertex id to its literal for quick lookup.
    vertex_literal: List[int] = []
    for clause in clauses:
        # Each clause is guaranteed to have exactly three literals.
        for lit in clause:
            vertex_literal.append(lit)

    # Compare each pair of vertices from different clauses.
    for i in range(num_clauses):
        for j in range(3):
            v1 = i * 3 + j
            lit1 = vertex_literal[v1]
            var1 = abs(lit1)
            sign1 = lit1 > 0
            # Only need to compare with later clauses to avoid duplicates.
            for i2 in range(i + 1, num_clauses):
                for j2 in range(3):
                    v2 = i2 * 3 + j2
                    lit2 = vertex_literal[v2]
                    if abs(lit2) != var1:
                        continue
                    # Complementary if signs differ.
                    if (lit2 > 0) != sign1:
                        add_edge(v1, v2)

    # The required independent set size is the number of clauses.
    k = num_clauses

    return {"n": n_vertices, "edges": edges, "k": k}

