"""Reduction from 3-SAT to Independent Set.

The source problem is :class:`ThreeSat` (defined in ``problems.py``) and the
target problem is :class:`IndependentSet`.  The reduction follows the classic
polynomial‑time construction:

* For each clause create a triangle (3 vertices, all mutually adjacent).  An
  independent set can contain at most one vertex from each triangle, which
  corresponds to picking a literal that satisfies the clause.
* For any two vertices whose literals are complementary (``v`` and ``-v``) add
  an edge.  This prevents an independent set from selecting both a variable
  and its negation, thus guaranteeing a consistent truth assignment.
* Set ``k`` (the required independent‑set size) to the number of clauses.

If the formula has no clauses it is trivially satisfiable; we return an empty
graph with ``k = 0`` – a yes instance of Independent Set because ``k <= 0``.

The implementation is straightforward and runs in polynomial time in the
size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import List, Tuple, Set

from problems import ThreeSat, IndependentSet


def _literal_opposite(l1: int, l2: int) -> bool:
    """Return ``True`` if ``l1`` is the negation of ``l2`` (e.g., 3 and -3)."""
    return l1 == -l2


def reduce(instance: dict) -> dict:
    """Reduce a 3‑SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary respecting the format of :class:`ThreeSat` – it must have
        the keys ``"num_vars"`` and ``"clauses"``.

    Returns
    -------
    dict
        An Independent Set instance (keys ``"n"``, ``"edges"`` and ``"k"``).
    """
    # Validate the source instance – this will raise InvalidInstance if malformed.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: empty formula – trivially satisfiable.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a unique vertex id to each literal occurrence.
    # ``vertex_info`` maps vertex id -> (clause_index, literal).
    vertex_info: List[Tuple[int, int]] = []  # (clause_idx, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_info.append((ci, lit))

    n_vertices = len(vertex_info)
    edge_set: Set[Tuple[int, int]] = set()

    # Helper to add an undirected edge without duplicates.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # 1. Intra‑clause edges – make each clause a triangle.
    # Vertices belonging to the same clause are contiguous in ``vertex_info``
    # because we added them clause by clause.
    for ci in range(num_clauses):
        base = ci * 3  # each clause has exactly 3 literals
        a, b, c = base, base + 1, base + 2
        add_edge(a, b)
        add_edge(a, c)
        add_edge(b, c)

    # 2. Conflict edges between complementary literals from different clauses.
    for i in range(n_vertices):
        ci_i, lit_i = vertex_info[i]
        for j in range(i + 1, n_vertices):
            ci_j, lit_j = vertex_info[j]
            # Skip pairs from the same clause – they are already fully connected.
            if ci_i == ci_j:
                continue
            if _literal_opposite(lit_i, lit_j):
                add_edge(i, j)

    # Convert edge set to the required list-of-lists format.
    edges = [[u, v] for (u, v) in sorted(edge_set)]

    return {"n": n_vertices, "edges": edges, "k": num_clauses}

