"""Reduction from 3‑SAT to Clique.

The source problem is :class:`ThreeSat` defined in ``problems.py``.
The target problem is :class:`Clique` also defined there.

For a 3‑CNF formula with ``c`` clauses we create a graph with ``3*c``
vertices – one vertex for each literal in each clause.  Two vertices are
connected by an edge iff they belong to *different* clauses and the two
corresponding literals are *compatible* (they do not contradict each
other, i.e. they are not ``x`` and ``-x`` for the same variable).

It is a classic textbook reduction: the formula is satisfiable iff the
graph contains a clique of size ``c`` (one vertex from each clause, all
pairwise compatible).  The construction runs in polynomial time and
produces a valid ``Clique`` instance.

Edge cases:
* If the formula has no clauses we output a graph with ``n = 0`` and
  ``k = 0`` – ``k <= 0`` is always a yes‑instance of Clique.
* The input is assumed to satisfy the validation rules of ``ThreeSat``;
  we nevertheless call ``ThreeSat.validate`` to raise a clear error on
  malformed data.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, Clique


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ``ThreeSat`` format:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.

    Returns
    -------
    dict
        A ``Clique`` instance ``{"n": n, "edges": [[u, v], ...], "k": k}``.
    """

    # Validate the source instance – this will raise InvalidInstance on bad input.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Trivial case: no clauses → always satisfiable.  Return a graph where k <= 0.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Each clause contributes three vertices.
    n = 3 * num_clauses
    k = num_clauses

    # Map (clause_index, position) -> vertex id.
    def vertex_id(ci: int, pos: int) -> int:
        return ci * 3 + pos

    edges: List[List[int]] = []

    # Build edges between compatible literals from different clauses.
    for i in range(num_clauses):
        for j in range(i + 1, num_clauses):
            clause_i = clauses[i]
            clause_j = clauses[j]
            for pi, lit_i in enumerate(clause_i):
                for pj, lit_j in enumerate(clause_j):
                    # Literals contradict if they refer to the same variable with opposite signs.
                    if abs(lit_i) == abs(lit_j) and lit_i == -lit_j:
                        continue  # incompatible, no edge
                    u = vertex_id(i, pi)
                    v = vertex_id(j, pj)
                    # Ensure u < v for consistency (Clique.validate expects undirected edges without duplicates).
                    if u > v:
                        u, v = v, u
                    edges.append([u, v])

    # Remove potential duplicate edges (should not happen with the construction, but be safe).
    seen = set()
    unique_edges: List[List[int]] = []
    for u, v in edges:
        key = frozenset((u, v))
        if key not in seen:
            seen.add(key)
            unique_edges.append([u, v])

    # Validate the target instance before returning.
    result = {"n": n, "edges": unique_edges, "k": k}
    Clique.validate(result)
    return result

