"""Reduction from Clique to Vertex Cover.

The reduction is the classic complement‑graph construction:

* Given a graph G = (V, E) and an integer k, we build the complement graph
  G' = (V, \overline{E}) where \overline{E} contains exactly those unordered
  vertex pairs that are **not** edges of G.
* A set C of vertices is a vertex cover of G' of size at most |V|-k iff the
  complement V\C is a clique of size at least k in G.

Therefore the instance (n, edges, k) of ``Clique`` is transformed into the
instance (n, complement_edges, n-k) of ``VertexCover``.  Edge‑cases line up
perfectly:

* k ≤ 0  →  n‑k ≥ n  →  VertexCover instance is trivially yes.
* k > n  →  n‑k < 0   →  VertexCover instance is trivially no.

The function validates the input using ``Clique.validate`` and returns a
dictionary that conforms to the ``VertexCover`` format.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, VertexCover


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the list of edges of the complement of a simple undirected graph.

    The input ``edges`` is assumed to be validated (no duplicates, no self‑loops).
    The output is a list of unordered pairs ``[u, v]`` with ``u < v``.
    """
    present = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        present.add((u, v))

    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent VertexCover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Clique instance as described in
        ``problems.Clique``.

    Returns
    -------
    dict
        A dictionary representing a VertexCover instance.  The instance is
        guaranteed to be valid according to ``VertexCover.validate`` and has
        the property that the original instance is a *yes* instance iff the
        returned instance is a *yes* instance.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement graph edges.
    comp_edges = _complement_edges(n, edges)

    # The vertex‑cover budget is n - k.
    new_k = n - k

    reduced = {"n": n, "edges": comp_edges, "k": new_k}
    # Ensure the produced instance is valid for the target problem.
    VertexCover.validate(reduced)
    return reduced

