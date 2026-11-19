"""Reduction from 3-SAT to Independent Set.

The reduction follows the classic construction:

* For each clause we create a triangle of three vertices, one for each
  literal in the clause.  Selecting at most one vertex from each triangle
  guarantees that at most one literal per clause is chosen.
* For any two vertices that correspond to complementary literals (e.g.
  ``x`` and ``-x``) we add an edge between them.  This prevents the
  independent set from containing both a variable and its negation.

If the original formula has ``C`` clauses, the constructed graph has
``3*C`` vertices and we ask whether it contains an independent set of size
at least ``C``.  An independent set of that size corresponds exactly to a
truth assignment satisfying all clauses, and vice‑versa.

The implementation validates the input using the problem classes defined
in ``problems.py`` and returns a dictionary that conforms to the
``IndependentSet`` instance format.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, IndependentSet


def _literal_edges(num_vertices: int, literals: List[int]) -> List[List[int]]:
    """Return edges that enforce the complement constraint.

    ``literals`` is a list indexed by vertex id containing the literal
    represented by that vertex.  For every pair of vertices whose literals
    are opposites we add an undirected edge.
    """
    edges: List[List[int]] = []
    for i in range(num_vertices):
        li = literals[i]
        for j in range(i + 1, num_vertices):
            if li == -literals[j]:
                edges.append([i, j])
    return edges


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        An ``IndependentSet`` instance ``{"n": n, "edges": [...], "k": k}``.
    """
    # Validate the source instance.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: no clauses – we can return an empty graph with k = 0.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Each clause contributes three vertices.
    n = 3 * num_clauses
    edges: List[List[int]] = []
    vertex_literals: List[int] = [0] * n

    # Build the triangle for each clause and store the literal for each vertex.
    for idx, clause in enumerate(clauses):
        base = idx * 3
        # clause is guaranteed to have exactly three literals by validation.
        for offset, lit in enumerate(clause):
            vertex = base + offset
            vertex_literals[vertex] = lit
        # add the three edges of the triangle (undirected, stored once)
        edges.append([base, base + 1])
        edges.append([base, base + 2])
        edges.append([base + 1, base + 2])

    # Add edges for complementary literals across different clauses.
    edges.extend(_literal_edges(n, vertex_literals))

    result = {"n": n, "edges": edges, "k": num_clauses}
    # Validate the target instance before returning.
    IndependentSet.validate(result)
    return result

