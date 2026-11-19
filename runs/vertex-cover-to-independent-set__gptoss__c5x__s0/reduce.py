"""Reduction from Vertex Cover to Independent Set.

The classic relationship between the two problems on the *same* graph is:

    A set C is a vertex cover  <=>  V \ C is an independent set.

Therefore a graph G has a vertex cover of size at most k iff it has an
independent set of size at least n - k, where n is the number of vertices.

The reduction is therefore trivial: keep the graph unchanged and map the
parameter k to k' = n - k.

The function ``reduce`` validates the source instance using the provided
``VertexCover.validate`` method, constructs the target instance and validates
it with ``IndependentSet.validate`` before returning it.
"""

from __future__ import annotations

from typing import Dict, List, Any

# Import the problem classes for validation.
from problems import VertexCover, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance with keys ``n``,
        ``edges`` and ``k``.

    Returns
    -------
    dict
        An Independent Set instance on the same graph with ``k' = n - k``.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute the new parameter for Independent Set.
    k_prime: int = n - k

    # Construct the target instance. The graph is unchanged.
    target_instance: Dict[str, Any] = {"n": n, "edges": edges.copy(), "k": k_prime}

    # Validate the target instance before returning – this catches any bugs
    # in the transformation.
    IndependentSet.validate(target_instance)
    return target_instance

