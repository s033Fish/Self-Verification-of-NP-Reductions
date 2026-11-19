"""Reduction from 3-SAT to Clique.

The source problem is :class:`ThreeSat` defined in ``problems.py``.
The target problem is :class:`Clique` defined in the same file.

For a 3‑SAT formula with ``c`` clauses we create a graph with ``3*c``
vertices – one vertex for each literal in each clause.  Vertices that come
from the *same* clause are never connected.  Vertices from *different*
clauses are connected iff the two literals are **compatible**, i.e. they do
not contradict each other (they are not the same variable with opposite
signs).

The produced instance has ``k = c``.  A clique of size at least ``c`` must
pick exactly one vertex from each clause, and the compatibility condition
ensures that the chosen literals can simultaneously be true.  Hence the
graph contains a clique of size ``c`` iff the original formula is
satisfiable.

Edge cases:
* If the formula has no clauses we set ``k = 0`` (always a yes‑instance) and
  produce an empty graph.
* The reduction runs in polynomial time – the graph has at most ``3*c``
  vertices and ``O(c^2)`` edges.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, Clique


def _compatible(lit1: int, lit2: int) -> bool:
    """Return ``True`` if the two literals can be true simultaneously.

    Two literals are incompatible only when they refer to the same
    variable with opposite signs, e.g. ``+x`` and ``-x``.
    """

    return not (abs(lit1) == abs(lit2) and (lit1 > 0) != (lit2 > 0))


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        An instance of the ``Clique`` problem such that the answers match.
    """

    # Validate the source instance – this will raise if malformed.
    ThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)

    # Edge case: no clauses – always satisfiable.  Return a trivial clique
    # instance with k = 0 (the definition guarantees a yes answer).
    if c == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a unique vertex id to each literal occurrence.
    # Vertex ids are 0 .. 3*c-1 in clause order.
    vertex_of = []  # List of (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertex_of.append((ci, lit))

    n = len(vertex_of)
    edges: List[List[int]] = []

    # Build edges between vertices of different clauses that are compatible.
    for i in range(n):
        ci, lit_i = vertex_of[i]
        for j in range(i + 1, n):
            cj, lit_j = vertex_of[j]
            if ci == cj:
                # Same clause – never connect.
                continue
            if _compatible(lit_i, lit_j):
                edges.append([i, j])

    # The target instance must satisfy its own validation.
    target_instance = {"n": n, "edges": edges, "k": c}
    Clique.validate(target_instance)
    return target_instance

