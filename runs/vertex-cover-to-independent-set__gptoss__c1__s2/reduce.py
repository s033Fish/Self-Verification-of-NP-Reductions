"""Reduction from Vertex Cover to Independent Set.

The source problem (VertexCover) asks whether a given undirected graph
has a vertex cover of size **at most** ``k``.  The target problem
(IndependentSet) asks whether the same graph has an independent set of
size **at least** ``k'``.

It is a classic textbook reduction: a set of vertices ``C`` is a vertex
cover of ``G`` iff its complement ``V \ C`` is an independent set of
``G``.  Therefore, ``G`` has a vertex cover of size ≤ ``k`` iff ``G``
has an independent set of size ≥ ``|V| - k``.

The ``reduce`` function receives an instance of the source problem in the
format defined in ``problems.py`` and returns an instance of the target
problem with the same graph and the transformed parameter ``k'``.

The transformation runs in linear time with respect to the size of the
input (simply copying the data and computing ``n - k``), which is
polynomial as required.
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Vertex Cover instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (number of vertices), ``"edges"``
        (list of ``[u, v]`` pairs) and ``"k"`` (the size bound for the
        vertex cover).

    Returns
    -------
    dict
        A new dictionary representing an Independent Set instance with the
        same vertices and edges, and ``k' = n - k``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The complement size for the independent set.
    k_prime: int = n - k

    # Return a fresh dictionary; we copy ``edges`` to avoid accidental
    # mutation of the original instance.
    return {
        "n": n,
        "edges": [list(e) for e in edges],
        "k": k_prime,
    }

