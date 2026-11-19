"""Reduction from 3‑SAT to Independent Set.

The source problem is :class:`ThreeSat` (see ``problems.py``).  An instance is a
dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each
literal is an integer ``+v`` (variable *v* true) or ``-v`` (variable *v* false).

The target problem is :class:`IndependentSet`.  Its instance format is
``{"n": n, "edges": [[u, v], ...], "k": k}`` where vertices are numbered
``0..n-1``.

Standard reduction:

* For each clause we create a triangle (3‑clique).  Selecting at most one
  vertex from each triangle guarantees we pick at most one literal per clause.
* For any two vertices whose literals are complementary (``x`` and ``-x``) we
  add an edge.  This prevents picking a contradictory pair of literals.
* We set ``k`` equal to the number of clauses.  An independent set of size ``k``
  corresponds exactly to a satisfying assignment: pick one vertex from each
  clause‑triangle, none of which are contradictory.

The construction runs in polynomial time – the graph has ``3·C`` vertices
(``C`` = number of clauses) and at most ``3·C`` intra‑clause edges plus a
quadratic number of contradiction edges.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A valid 3‑SAT instance as described in the docstring of
        :class:`ThreeSat`.

    Returns
    -------
    dict
        An Independent Set instance ``{"n": n, "edges": [...], "k": k}`` such
        that the original instance is satisfiable **iff** the returned graph has
        an independent set of size at least ``k``.
    """

    # Extract clauses; each clause already contains exactly three literals.
    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Vertex numbering: clause i contributes vertices 3*i, 3*i+1, 3*i+2.
    # Store the literal represented by each vertex for later contradiction edges.
    vertex_literal: List[int] = []
    for clause in clauses:
        # clause is a list of three literals (ints)
        vertex_literal.extend(clause)

    n_vertices = len(vertex_literal)
    edges: List[List[int]] = []

    # 1. Intra‑clause edges – make each clause a triangle (3‑clique).
    for i in range(num_clauses):
        a = 3 * i
        b = a + 1
        c = a + 2
        edges.append([a, b])
        edges.append([a, c])
        edges.append([b, c])

    # 2. Contradiction edges: connect vertices whose literals are opposite.
    #    Since a clause never contains both v and -v, any such pair must be from
    #    different clauses.
    for i in range(n_vertices):
        lit_i = vertex_literal[i]
        for j in range(i + 1, n_vertices):
            if lit_i == -vertex_literal[j]:
                edges.append([i, j])

    return {"n": n_vertices, "edges": edges, "k": num_clauses}

