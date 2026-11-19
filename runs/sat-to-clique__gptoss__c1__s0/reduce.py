"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem (SAT) is defined in ``problems.py`` with the following
instance format (reproduced here for reference):

    {
        "num_vars": m,
        "clauses": [[literal, ...], ...]
    }

Literals are encoded as signed integers: ``+v`` means variable ``v`` is true,
``-v`` means variable ``v`` is false.  Clauses may be empty, may contain
duplicate literals, and may even contain both a literal and its negation.

The target problem (Clique) expects an instance of the form:

    {
        "n": n,               # number of vertices (0‑indexed)
        "edges": [[u, v], ...],
        "k": k                # size threshold for the clique
    }

We implement the classic polynomial‑time many‑one reduction:

* For each clause *C_i* and each literal *ℓ* in *C_i* we create a vertex
  ``v(i, ℓ)``.
* Vertices belonging to the same clause are never connected.
* Vertices from different clauses are connected **iff** the corresponding
  literals are *compatible*, i.e. they do not force a variable to be both
  true and false.  Formally, two literals ``ℓ₁`` and ``ℓ₂`` are incompatible
  exactly when ``abs(ℓ₁) == abs(ℓ₂)`` and ``ℓ₁ == -ℓ₂``.
* The parameter ``k`` of the Clique instance is set to the number of clauses.

Correctness sketch:
    • If the SAT formula is satisfiable, pick for each clause a literal that
      is true under a satisfying assignment.  The selected vertices are pair‑
      wise compatible, hence they form a ``k``‑clique.
    • Conversely, any ``k``‑clique must contain exactly one vertex from each
      clause (otherwise two vertices would share a clause and lack an edge).
      The literals represented by the clique cannot be pair‑wise contradictory,
      thus they define a consistent truth assignment satisfying every clause.

Edge cases handled explicitly:
    – Zero clauses: the formula is trivially satisfiable.  We output a graph
      with ``k = 0`` (always a yes‑instance of Clique).
    – Empty clause: such a clause contributes no vertices, making the graph
      have fewer than ``k`` vertices, so a ``k``‑clique cannot exist – the
      reduction correctly yields a no‑instance.

The implementation runs in O(V²) time where V is the total number of literals
across all clauses, which is polynomial in the size of the SAT instance.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a SAT formula as described above.

    Returns
    -------
    dict
        A Clique instance dictionary ``{"n": ..., "edges": ..., "k": ...}``
        that is a yes‑instance iff the input SAT instance is a yes‑instance.
    """

    # Extract clauses; the number of variables is irrelevant for the reduction.
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: no clauses → trivially satisfiable.  Use k = 0 which is always
    # a yes‑instance of Clique regardless of the graph.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build a list of vertices.  Each vertex is identified by its index in this
    # list.  We store a tuple (clause_index, literal) for later compatibility
    # checks.
    vertices: List[tuple[int, int]] = []
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)
    edges: List[List[int]] = []

    # Helper to decide if two literals are compatible.
    def compatible(lit1: int, lit2: int) -> bool:
        # They are incompatible only when they refer to the same variable with
        # opposite polarity.
        return not (abs(lit1) == abs(lit2) and lit1 == -lit2)

    # Add edges between vertices from different clauses that are compatible.
    for i in range(n):
        ci, li = vertices[i]
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci == cj:
                continue  # same clause – no edge
            if compatible(li, lj):
                edges.append([i, j])

    # The target Clique instance.
    return {"n": n, "edges": edges, "k": num_clauses}

