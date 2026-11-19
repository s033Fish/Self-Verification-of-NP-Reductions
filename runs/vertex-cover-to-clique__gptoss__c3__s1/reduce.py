"""Reduction from Vertex Cover to Clique.

The source problem is :class:`VertexCover` (instance format {"n": int,
"edges": [[u, v], ...], "k": int}).  The target problem is :class:`Clique`
with the same format.

Standard reduction:

* A set C is a vertex cover of size at most *k* in a graph G = (V, E) iff the
  complement V\C is an independent set of size at least |V| - k.
* An independent set in a graph is a clique in its complement.

Therefore we construct the complement graph G̅ and ask whether it contains a
clique of size at least ``n - k``.

The transformation is polynomial‑time (quadratic in the number of vertices)
and preserves the answer for all edge cases, as explained in the docstring.
"""

from __future__ import annotations

from typing import Dict, List

# Import the problem classes to reuse validation helpers if desired.
from problems import SOURCE as VertexCover, TARGET as Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of an undirected graph.

    ``edges`` is assumed to be a list of unordered pairs ``[u, v]`` with
    ``0 <= u < v < n`` and no duplicates.  The result is a list of pairs ``[u,
    v]`` (also with ``u < v``) representing all non‑edges of the original
    graph.
    """
    # Build a set of existing edges for O(1) membership tests.
    existing = {frozenset(edge) for edge in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the Vertex Cover specification.

    Returns
    -------
    dict
        A Clique instance such that ``Clique.is_yes`` on the returned value
        is true exactly when ``VertexCover.is_yes`` on the input is true.
    """
    # Ensure the source instance is well‑formed (will raise InvalidInstance if
    # not).  This also guarantees the presence of the required keys.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement graph edges.
    comp_edges = _complement_edges(n, edges)

    # Target clique size: n - k (as explained above).
    target_k = n - k

    reduced_instance: Dict = {"n": n, "edges": comp_edges, "k": target_k}
    # Validate the produced instance for safety.
    Clique.validate(reduced_instance)
    return reduced_instance

