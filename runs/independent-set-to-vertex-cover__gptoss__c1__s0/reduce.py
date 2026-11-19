"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) asks whether a given undirected graph
has an independent set of size *at least* ``k``.  The target problem (Vertex Cover)
asks whether the same graph has a vertex cover of size *at most* ``k'``.

The classic polynomial‑time reduction is based on the observation that a set
``S`` of vertices is independent in ``G`` iff its complement ``V \ S`` is a
vertex cover of ``G``.  Consequently, an independent set of size ``k`` exists
iff a vertex cover of size ``|V| - k`` exists.

The ``reduce`` function implements this transformation.  It receives an
instance of ``IndependentSet`` – a dictionary with keys ``"n"``, ``"edges"``
and ``"k"`` – and returns a dictionary that conforms to the ``VertexCover``
specification, using the same vertices and edges and adjusting the budget
parameter accordingly.

The transformation runs in linear time with respect to the size of the input
instance (simply copying the edge list and performing a constant‑time integer
computation), satisfying the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary representing an Independent Set instance with the
        following fields:
        * ``"n"`` (int): number of vertices, labelled ``0 .. n-1``.
        * ``"edges"`` (list[list[int]]): undirected edge list.
        * ``"k"`` (int): required size of the independent set (at least ``k``).

    Returns
    -------
    dict
        A Vertex Cover instance that is a yes‑instance exactly when the input
        instance is a yes‑instance.  The returned dictionary contains the same
        ``"n"`` and ``"edges"`` fields and a transformed budget ``k' = n - k``.
    """

    # Extract required fields.  The problem definitions guarantee the keys
    # exist and have the correct types, so we do not perform exhaustive
    # validation here – the surrounding benchmark harness will call the
    # appropriate ``validate`` methods if needed.
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The reduction: complement the independent‑set budget.
    k_prime: int = n - k

    # Return a new instance dictionary.  ``edges`` is a list of lists; we can
    # reuse it directly because the specification treats the instance as
    # immutable for the purpose of the reduction.
    return {
        "n": n,
        "edges": edges,
        "k": k_prime,
    }

