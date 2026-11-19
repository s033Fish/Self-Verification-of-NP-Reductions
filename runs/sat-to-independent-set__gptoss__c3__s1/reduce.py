"""Reduction from SAT (CNF satisfiability) to Independent Set.

The reduction follows the classic textbook construction:

* For each clause we create a *clique* – every literal in the clause becomes a
  vertex and all vertices of the same clause are pairwise adjacent.  Selecting
  at most one vertex from each clause guarantees that the chosen vertices do
  not belong to the same clause.
* Vertices belonging to different clauses are connected when the corresponding
  literals are complementary (e.g. ``x`` and ``¬x``).  This prevents the
  independent set from containing both a variable and its negation.

With ``k`` set to the number of clauses, an independent set of size ``k``
exists **iff** the original formula is satisfiable.

Edge‑case handling mirrors the specification in ``problems.py``:

* A formula with *no* clauses is trivially satisfiable – we output a graph with
  ``k = 0`` which is always a yes‑instance.
* A formula containing an *empty* clause is unsatisfiable – we output a graph
  with ``n = 0`` and ``k`` equal to the number of clauses (≥ 1).  Because ``k >
  n`` the independent‑set instance is a definite no‑instance.

The implementation runs in polynomial time in the size of the SAT instance.
"""

from __future__ import annotations

from typing import List, Tuple

from problems import Sat, IndependentSet


def _complement(lit1: int, lit2: int) -> bool:
    """Return ``True`` if ``lit1`` and ``lit2`` are complementary literals.

    Complementary means they refer to the same variable with opposite signs,
    e.g. ``+3`` and ``-3``.
    """
    return lit1 == -lit2


def reduce(instance: dict) -> dict:
    """Reduce a SAT instance to an Independent‑Set instance.

    The returned dictionary conforms to the format required by
    ``IndependentSet.validate``:

    ``{"n": <int>, "edges": [[u, v], ...], "k": <int>}``
    """
    # Validate the SAT instance (will raise InvalidInstance if malformed).
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge cases -----------------------------------------------------------
    # 1. Empty clause → unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        # No vertices, k > n ensures a NO answer.
        return {"n": 0, "edges": [], "k": max(1, num_clauses)}

    # 2. No clauses → trivially satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # General case --------------------------------------------------------
    # Assign a unique vertex id to each literal occurrence.
    vertex_id = 0
    # For each clause store a list of (vertex_id, literal).
    clause_vertices: List[List[Tuple[int, int]]] = []
    for clause in clauses:
        current: List[Tuple[int, int]] = []
        for lit in clause:
            current.append((vertex_id, lit))
            vertex_id += 1
        clause_vertices.append(current)

    n_vertices = vertex_id
    edge_set: set[frozenset[int]] = set()

    # 1. Make each clause a clique.
    for verts in clause_vertices:
        ids = [vid for vid, _ in verts]
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                edge_set.add(frozenset((ids[i], ids[j])))

    # 2. Add edges between complementary literals from different clauses.
    #    We iterate over all pairs of clauses to stay polynomial.
    for i in range(num_clauses):
        for j in range(i + 1, num_clauses):
            for vid1, lit1 in clause_vertices[i]:
                for vid2, lit2 in clause_vertices[j]:
                    if _complement(lit1, lit2):
                        edge_set.add(frozenset((vid1, vid2)))

    # Convert edge set to the required list-of-lists representation.
    edges = [[u, v] for u, v in (tuple(e) for e in edge_set)]

    return {"n": n_vertices, "edges": edges, "k": num_clauses}

