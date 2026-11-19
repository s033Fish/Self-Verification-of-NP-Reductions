"""Reduction from Clique to Vertex Cover.

The reduction is the classic one based on graph complement:

* A set of vertices forms a *clique* in a graph G iff it forms an
  *independent set* in the complement graph G̅.
* For any graph on ``n`` vertices, the size of a minimum vertex cover plus
  the size of a maximum independent set equals ``n``.

Therefore, G has a clique of size at least ``k`` iff the complement of G has
an independent set of size at least ``k`` iff the complement of G has a vertex
cover of size at most ``n - k``.

The ``reduce`` function implements this transformation.  It validates the
input using the source problem class, constructs the complement edge list, and
produces an instance of the target problem with ``k' = n - k``.

Edge‑case handling follows directly from the formulas:

* ``k <= 0`` → ``k' >= n`` → VertexCover instance is trivially a *yes*.
* ``k > n`` → ``k' < 0`` → VertexCover instance is trivially a *no*.

Both match the specifications of the source problem.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Clique, VertexCover


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is assumed to be a valid list for a graph on ``n`` vertices.
    The result contains each unordered pair ``[u, v]`` with ``u < v`` that is
    *not* present in ``edges``.
    """
    # Create a set of frozensets for O(1) membership checks.
    existing = {frozenset(e) for e in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a VertexCover instance.

    The returned dictionary follows the exact format required by the
    ``VertexCover`` problem class (keys ``"n"``, ``"edges"`` and ``"k"``).
    """
    # Validate source instance – will raise InvalidInstance on malformed input.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement graph edges.
    comp_edges = _complement_edges(n, edges)

    # Transform the size parameter.
    k_target = n - k

    # Build the target instance.
    target_instance: Dict = {"n": n, "edges": comp_edges, "k": k_target}

    # Validate target instance for safety (optional but helpful during testing).
    VertexCover.validate(target_instance)
    return target_instance

