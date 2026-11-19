"""Reduction from 3-SAT to Clique.

The source problem is :class:`ThreeSat` (see ``problems.py``) and the target
problem is :class:`Clique`.

For a 3‑SAT instance with ``c`` clauses we create a graph with ``3*c``
vertices – one vertex for each literal in each clause.  Vertices belonging to the same clause are never connected.  Vertices from different clauses are
connected by an edge iff the two literals are **compatible**, i.e. they are
not complementary (``x`` and ``-x`` for the same variable).  The reduction
asks whether the graph contains a clique of size ``c``.

Correctness sketch:
* If the formula is satisfiable, pick a true literal from each clause.  Those
  literals are pairwise compatible, hence the corresponding vertices form a
  clique of size ``c``.
* Conversely, any clique of size ``c`` must contain exactly one vertex from
  each clause (otherwise two vertices would belong to the same clause and be
  non‑adjacent).  The literals represented by the vertices are pairwise
  compatible, therefore we can assign each variable the truth value that
  satisfies all chosen literals – this yields a satisfying assignment.

Edge cases:
* An instance with no clauses is trivially satisfiable.  We map it to a graph
  with ``n = 0`` vertices, no edges and ``k = 0``.  By the definition of Clique
  this is a yes‑instance.
* The reduction runs in polynomial time – the graph has at most ``3*c``
  vertices and ``O(c^2)`` edges.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, Clique


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary that conforms to :class:`ThreeSat`'s format.

    Returns
    -------
    dict
        A dictionary that conforms to :class:`Clique`'s format.
    """
    # Validate the source instance – this will raise if malformed.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]  # type: ignore[assignment]
    num_clauses = len(clauses)

    # Edge case: no clauses → always satisfiable. Return a trivial graph.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a unique vertex id to each literal occurrence.
    # We store (clause_index, literal) for each vertex.
    vertex_info: List[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_info.append((ci, lit))

    n = len(vertex_info)
    edges: List[List[int]] = []

    # Build edges between vertices of different clauses if literals are compatible.
    for i in range(n):
        ci, li = vertex_info[i]
        for j in range(i + 1, n):
            cj, lj = vertex_info[j]
            if ci == cj:
                # Same clause – not allowed in a clique.
                continue
            # literals are compatible unless they are complementary.
            if li == -lj:
                continue
            edges.append([i, j])

    # The target asks for a clique of size equal to the number of clauses.
    k = num_clauses

    result = {"n": n, "edges": edges, "k": k}
    # Validate the target instance before returning.
    Clique.validate(result)
    return result

