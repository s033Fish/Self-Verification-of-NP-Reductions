"""Reduction from Vertex Cover to Clique.

The source problem is :class:`VertexCover` and the target problem is
``Clique``.  Both problems are defined in ``problems.py`` and follow the
instance format described in the task description:

* ``{"n": n, "edges": [[u, v], ...], "k": k}``
* ``n`` – number of vertices (0‑based indices)
* ``edges`` – list of undirected edges, each appears only once
* ``k`` – integer parameter of the decision problem

The classic polynomial‑time reduction works via the graph complement:

* A set ``C`` is a vertex cover of size ``k`` in ``G`` iff the complement of
  ``C`` is an independent set of size ``n‑k``.
* An independent set in ``G`` is exactly a clique in the complement graph
  ``G̅``.

Therefore ``G`` has a vertex cover of size at most ``k`` ⇔ ``G̅`` has a
clique of size at least ``n‑k``.

The reduction builds the complement graph and adjusts the parameter
accordingly.  Edge cases (negative ``k``, ``k`` ≥ ``n``) are handled
automatically because the transformed instance respects the target's
edge‑case definitions.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem definitions.  They provide ``validate`` and ``is_yes``
# methods used by the test harness.
from problems import VertexCover, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of a simple undirected graph.

    ``edges`` is assumed to be a valid edge list for a graph on ``n``
    vertices (no self‑loops, no duplicates).  The result contains each
    unordered pair ``[u, v]`` with ``u < v`` that is **not** present in the
    original list.
    """
    existing = {frozenset(e) for e in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    The function validates the input, constructs the complement graph, and
    returns a new instance respecting the ``Clique`` specification.  The
    transformation runs in ``O(n^2)`` time, which is polynomial in the size
    of the input.
    """
    # Ensure the source instance is well‑formed.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement graph edges.
    comp_edges = _complement_edges(n, edges)

    # Parameter transformation: vertex cover of size ≤ k ↔ clique of size ≥ n‑k.
    new_k = n - k

    new_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": new_k}

    # Validate the produced target instance (helps catch programming errors).
    Clique.validate(new_instance)
    return new_instance

