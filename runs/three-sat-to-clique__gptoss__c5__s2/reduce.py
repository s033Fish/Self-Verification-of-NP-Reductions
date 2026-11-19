"""Reduction from 3‑SAT to Clique.

The source problem is :class:`ThreeSat` (defined in ``problems.py``) with
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.
The target problem is :class:`Clique` with instance format
``{"n": n, "edges": [[u, v], ...], "k": k}``.

For a formula with *c* clauses we create a graph with ``3*c`` vertices – one
vertex for each literal in each clause.  Vertices belonging to the same
clause are never connected.  Vertices from different clauses are connected
iff the corresponding literals are **not** contradictory, i.e. they do not
represent the same variable with opposite signs.  Setting ``k = c`` yields
the classic polynomial‑time reduction: the formula is satisfiable iff the
graph contains a clique of size at least ``c``.

Edge‑case handling:
* If the formula has no clauses the answer is trivially *yes*.  We return a
  Clique instance with ``k = 0`` – by definition any graph (including the
  empty graph) has a clique of size ``0``.

The function runs in time ``O(c^2)`` which is polynomial in the size of the
input.
"""

from __future__ import annotations

from typing import Dict, List

from problems import SOURCE, TARGET


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``Clique`` format such that the
        3‑SAT instance is satisfiable iff the produced graph has a clique of
        size at least ``k``.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.
    SOURCE.validate(instance)  # type: ignore[attr-defined]

    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)

    # Edge case: no clauses → trivially satisfiable.
    if c == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a vertex id to each literal in each clause.
    # vertex_id = clause_index * 3 + literal_index (0‑based).
    n = c * 3
    edges: List[List[int]] = []

    # Pre‑compute the literals for each vertex for quick lookup.
    vertex_literal: List[int] = []  # index -> literal value
    for clause in clauses:
        # each clause has exactly 3 literals by validation
        vertex_literal.extend(clause)

    # Build edges between vertices of different clauses when they are not
    # contradictory.
    for i in range(n):
        clause_i = i // 3
        lit_i = vertex_literal[i]
        for j in range(i + 1, n):
            clause_j = j // 3
            if clause_i == clause_j:
                # Same clause – never connect.
                continue
            lit_j = vertex_literal[j]
            # Contradictory if same variable with opposite signs.
            if abs(lit_i) == abs(lit_j) and lit_i != lit_j:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": c}

