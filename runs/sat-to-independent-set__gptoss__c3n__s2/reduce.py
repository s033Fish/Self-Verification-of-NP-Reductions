"""Reduction from SAT to Independent Set.

This file defines a single function ``reduce(instance)`` that takes a SAT
instance (as defined by the ``Sat`` class in ``problems.py``) and returns an
Independent Set instance (as defined by ``IndependentSet``). The reduction
is the classic one used in textbooks:

* For each clause we create a *clique* – a complete sub‑graph – whose vertices
  correspond to the literals of that clause.
* Vertices that represent complementary literals (e.g. ``+x`` and ``-x``) are
  connected by an edge, even if they belong to different clauses.
* The target parameter ``k`` is set to the number of clauses. An independent
  set of size at least ``k`` must therefore pick exactly one vertex from each
  clause, and the chosen literals cannot contradict each other – this is
  precisely a satisfying assignment of the original formula.

The reduction handles all edge cases described in the problem statements:

* An empty formula (no clauses) is always satisfiable. The reduction returns a
  graph with ``n = 0`` vertices, no edges and ``k = 0`` – which is a yes‑instance
  of Independent Set because ``k <= 0`` is always yes.
* A formula containing an empty clause cannot be satisfied. The reduction
  creates a graph where the corresponding clause contributes **no** vertices.
  Consequently the maximum independent set size is strictly less than the
  number of clauses, yielding a no‑instance.

The implementation validates the input using ``Sat.validate`` and constructs
the output dictionary that conforms to the ``IndependentSet`` format.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set

from problems import Sat, IndependentSet

def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a SAT formula with keys ``"num_vars"`` and
        ``"clauses"`` as described in ``problems.py``.

    Returns
    -------
    dict
        An Independent Set instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """

    # Validate the SAT instance first – this raises InvalidInstance on error.
    Sat.validate(instance)

    num_vars: int = instance["num_vars"]  # not used directly but kept for clarity
    clauses: List[List[int]] = instance["clauses"]

    # ``k`` is the number of clauses (including possible empty ones).
    k: int = len(clauses)

    # Build vertices. Each vertex corresponds to a literal occurrence.
    # We store a list of (clause_index, literal) for later edge construction.
    vertices: List[Tuple[int, int]] = []  # (clause_idx, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n: int = len(vertices)

    # Edge construction – we use a set of frozensets to avoid duplicates.
    edge_set: Set[frozenset[int]] = set()

    # Helper to add an undirected edge.
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        edge_set.add(frozenset((u, v)))

    # 1. Connect all pairs of vertices that belong to the same clause (clique).
    start = 0
    for clause in clauses:
        size = len(clause)
        # vertices for this clause are at positions [start, start+size)
        for i in range(start, start + size):
            for j in range(i + 1, start + size):
                add_edge(i, j)
        start += size

    # 2. Connect complementary literals across different clauses.
    #    Two literals are complementary if they have the same variable index
    #    and opposite signs, i.e., lit1 == -lit2.
    for i in range(n):
        ci1, lit1 = vertices[i]
        for j in range(i + 1, n):
            ci2, lit2 = vertices[j]
            # Skip pairs from the same clause – already handled above.
            if ci1 == ci2:
                continue
            if lit1 == -lit2:
                add_edge(i, j)

    # Convert edge_set to the required list of [u, v] pairs.
    edges: List[List[int]] = [list(edge) for edge in edge_set]

    # Construct the Independent Set instance.
    result: Dict = {"n": n, "edges": edges, "k": k}

    # Validate the produced instance (optional but helpful for debugging).
    IndependentSet.validate(result)
    return result

