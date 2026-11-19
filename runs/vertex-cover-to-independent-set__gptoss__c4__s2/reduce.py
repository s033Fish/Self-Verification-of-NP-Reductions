"""Reduction from Vertex Cover to Independent Set.

The classic relationship between the two problems on the same graph is:

    S is a vertex cover  <=>  V \ S is an independent set.

Therefore a graph G with a vertex cover of size at most k exists iff G has
an independent set of size at least n - k, where n is the number of vertices.

The reduction is therefore trivial: keep the graph unchanged and transform the
parameter k to n - k.

The function validates the source instance using the provided ``VertexCover``
class and returns a dictionary that conforms to the ``IndependentSet``
instance format.
"""

from __future__ import annotations

from typing import Dict, Any

from problems import VertexCover, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a VertexCover instance. It must contain the
        keys ``"n"``, ``"edges"`` and ``"k"`` as specified in the problem
        definition.

    Returns
    -------
    dict
        An IndependentSet instance with the same ``n`` and ``edges`` and with
        ``k`` transformed to ``n - k``.
    """
    # Validate the source instance. This will raise InvalidInstance if malformed.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges = instance["edges"]
    k: int = instance["k"]

    # Compute the target parameter.
    target_k = n - k

    # Build the target instance.
    target_instance: Dict[str, Any] = {"n": n, "edges": edges, "k": target_k}

    # Validate the produced instance to ensure we respect the specification.
    IndependentSet.validate(target_instance)
    return target_instance

