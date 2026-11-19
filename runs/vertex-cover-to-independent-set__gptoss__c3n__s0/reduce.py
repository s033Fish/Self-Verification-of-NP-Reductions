"""Reduction from Vertex Cover to Independent Set.

The reduction is the classic complement construction:

Given a graph G = (V, E) and an integer k, there exists a vertex cover
of size at most k iff the complement of that cover (i.e., V \ C) is an
independent set of size at least |V| - k.  Therefore we can map a
VertexCover instance to an IndependentSet instance by keeping the same
graph and setting the new target size to ``n - k``.

The function ``reduce`` validates the source instance using the provided
``VertexCover.validate`` method and returns a dictionary that conforms to
the ``IndependentSet`` format.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import VertexCover, IndependentSet

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a VertexCover instance. It must contain
        the keys ``"n"``, ``"edges"`` and ``"k"`` as described in the
        problem statement.

    Returns
    -------
    dict
        An IndependentSet instance with the same vertex set and edge list,
        but with ``k' = n - k``.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The target k is the size of the complement of a vertex cover of size k.
    target_k = n - k

    # Build the target instance. The IndependentSet class expects the same
    # fields as VertexCover (n, edges, k).
    target_instance: Dict[str, Any] = {"n": n, "edges": edges, "k": target_k}

    # Validate the produced instance to catch any accidental mistakes.
    IndependentSet.validate(target_instance)
    return target_instance

