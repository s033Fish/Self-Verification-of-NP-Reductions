"""Reduction from Independent Set to Vertex Cover.

The source problem (``IndependentSet``) asks whether a given undirected
graph with ``n`` vertices contains an *independent set* of size at least ``k``.
The target problem (``VertexCover``) asks whether the same graph contains a
*vertex cover* of size at most ``k'``.

It is a classic textbook reduction: a set of vertices is independent iff its
complement is a vertex cover.  Therefore an independent set of size ``k``
exists ⇔ a vertex cover of size ``n - k`` exists.

The ``reduce`` function implements this transformation.  It receives an
instance of the source problem as a dictionary with the keys ``"n"``,
``"edges"`` and ``"k"`` and returns a new dictionary in the exact format
expected by the target problem.  The transformation runs in linear time in
the size of the input (simply copying the edge list and computing ``n - k``).

Edge‑case handling follows automatically from the formula:

* If ``k <= 0`` the source answer is always *yes*.  The target instance gets
  ``k' = n - k >= n``; according to the target definition a cover of size
  ``>= n`` is always a *yes* instance.
* If ``k > n`` the source answer is always *no*.  Then ``k' = n - k < 0`` and
  the target problem declares any instance with a negative ``k`` to be *no*.
* When the graph has no edges the transformation still works because the
  edge list is copied unchanged.

The implementation does not import the problem classes themselves – the
testing harness will import ``reduce`` and call it directly.  No solver is
invoked, keeping the reduction purely polynomial‑time.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Transform an Independent Set instance into a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int), ``"edges"`` (list of [u, v]
        pairs) and ``"k"`` (int) representing the Independent Set problem.

    Returns
    -------
    dict
        An instance for the Vertex Cover problem with the same vertex set and
        edges, and with ``k' = n - k``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The complement size gives the vertex‑cover bound.
    k_prime: int = n - k

    # Return a new dictionary; we deliberately copy the edge list to avoid
    # accidental mutation of the original instance.
    return {
        "n": n,
        "edges": [list(e) for e in edges],
        "k": k_prime,
    }

