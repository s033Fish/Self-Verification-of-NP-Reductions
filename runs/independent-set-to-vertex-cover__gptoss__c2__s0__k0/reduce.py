"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) asks whether a given undirected
graph G = (V, E) contains an independent set of size at least ``k``.  The
target problem (Vertex Cover) asks whether G contains a vertex cover of
size at most ``k``.

The classic polynomial‑time reduction uses the complement relationship:
A set S \subseteq V is independent in G iff V \ S is a vertex cover of G.
Hence, G has an independent set of size \ge k \iff G has a vertex cover
of size \le |V|-k.

The ``reduce`` function implements this transformation.  It receives an
instance of the source problem – a dictionary with keys ``"n"``,
``"edges"`` and ``"k"`` – and returns a new dictionary in the target
format with the same vertex count and edge list, but with the parameter
``k`` replaced by ``n - k``.

All edge cases are handled automatically because the relationship
preserves the trivial yes/no conditions described in the problem
specifications:

* ``k <= 0`` (independent‑set always yes) → ``n - k >= n`` (vertex‑cover
  always yes because ``k >= n`` is a guaranteed yes).
* ``k > n`` (independent‑set always no) → ``n - k < 0`` (vertex‑cover
  always no because ``k < 0`` is a guaranteed no).
* Empty edge set – the transformation does not modify the graph, so the
  answers remain equivalent.

The transformation runs in O(1) time aside from copying the edge list,
which is linear in the size of the input and therefore polynomial.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        A dictionary representing an Independent Set instance with keys:
        ``"n"`` (int), ``"edges"`` (list of [u, v] pairs), and ``"k"`` (int).

    Returns
    -------
    dict
        A Vertex Cover instance with the same ``n`` and ``edges`` and
        ``k`` replaced by ``n - k``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The reduction: complement the size parameter.
    new_k = n - k

    # Return a new dict in the target format.
    return {"n": n, "edges": edges, "k": new_k}
