"""Reduction from 3‑SAT to Clique.

The source problem (``ThreeSat``) is described in ``problems.py`` as a
dictionary with keys ``"num_vars"`` and ``"clauses"``.  Each clause is a list
of three *literals* where a literal is an integer ``+v`` (meaning variable ``v``
is true) or ``-v`` (meaning variable ``v`` is false).  The instance is
*satisfiable* iff there exists a truth assignment that makes at least one
literal true in every clause.

The target problem (``Clique``) expects a graph given by ``"n"`` (number of
vertices), ``"edges"`` (list of unordered pairs ``[u, v]`` with ``0 <= u, v < n``)
and an integer ``"k"``.  The answer is *yes* iff the graph contains a clique of
size **at least** ``k``.

Standard polynomial‑time reduction:

* For each clause we create three vertices – one for each literal.  Thus the
  graph has ``n = 3 * m`` vertices where ``m`` is the number of clauses.
* Vertices belonging to the **same** clause are never connected (a clique must
  pick at most one literal per clause).
* Vertices from **different** clauses are connected exactly when the two
  corresponding literals are *compatible*, i.e. they are not complementary
  ``v`` and ``-v``.  Formally, literals ``ℓ₁`` and ``ℓ₂`` are compatible iff
  ``abs(ℓ₁) != abs(ℓ₂)`` or ``ℓ₁ == ℓ₂``.
* The required clique size is ``k = m`` (one vertex from each clause).

Correctness sketch:
    *If the SAT instance is satisfiable*, pick a true literal from each clause.
    The chosen vertices are pairwise compatible, therefore they form a
    ``k``‑clique.
    *Conversely*, a ``k``‑clique must contain exactly one vertex from each
    clause (otherwise two vertices from the same clause would be present and
    there would be no edge).  The literals labelling these vertices cannot be
    contradictory, so assigning each selected literal to true satisfies all
    clauses.

Edge cases:
    *If there are no clauses* the formula is trivially satisfiable.  We output a
    graph with ``n = 0`` vertices and ``k = 0`` – the Clique problem answers
    *yes* for ``k <= 0``.

The implementation below follows the description exactly and runs in
polynomial time.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _compatible(lit1: int, lit2: int) -> bool:
    """Return ``True`` if the two literals can both be true.

    Two literals are incompatible only when they refer to the same variable
    with opposite polarity, i.e. ``lit1 == -lit2``.
    """

    # ``lit1`` and ``lit2`` are non‑zero integers.
    return not (abs(lit1) == abs(lit2) and lit1 == -lit2)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of integers).

    Returns
    -------
    dict
        A Clique instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: empty formula – always satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Each clause contributes exactly three vertices.
    n = 3 * num_clauses
    k = num_clauses

    # Map (clause_index, literal_position) -> vertex id.
    # vertex_id = clause_index * 3 + literal_position
    edges: List[List[int]] = []
    # Build edges between compatible literals from different clauses.
    for i in range(num_clauses):
        clause_i = clauses[i]
        for li_pos, lit_i in enumerate(clause_i):
            vi = i * 3 + li_pos
            # Compare with later clauses to avoid duplicate edges.
            for j in range(i + 1, num_clauses):
                clause_j = clauses[j]
                for lj_pos, lit_j in enumerate(clause_j):
                    vj = j * 3 + lj_pos
                    if _compatible(lit_i, lit_j):
                        # Store edge with smaller vertex first for consistency.
                        if vi < vj:
                            edges.append([vi, vj])
                        else:
                            edges.append([vj, vi])

    return {"n": n, "edges": edges, "k": k}


__all__ = ["reduce"]

