"""Reduction from Independent Set to Vertex Cover.

The classic reduction uses the complement relationship: a set S is an
independent set in a graph G = (V, E) iff V \ S is a vertex cover of G.

Therefore, an instance (n, edges, k) of Independent Set is a *yes* instance
iff the instance (n, edges, n - k) of Vertex Cover is a *yes* instance.

The function ``reduce`` validates the source instance using the provided
``IndependentSet.validate`` method and then returns a new dictionary that
conforms to the ``VertexCover`` format.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import IndependentSet, VertexCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys "n", "edges" and "k" representing a
        graph and the required independent‑set size.

    Returns
    -------
    dict
        A new instance for the Vertex Cover problem with the same graph and a
        parameter ``k' = n - k``.

    The reduction runs in linear time with respect to the size of the input
    (the list of edges) and therefore satisfies the polynomial‑time
    requirement.
    """
    # Validate the source instance; this will raise InvalidInstance on malformed
    # input, matching the behaviour expected by the benchmark harness.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The complement size for the vertex‑cover instance.
    k_prime = n - k

    # Construct the target instance. The graph is unchanged.
    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": edges,
        "k": k_prime,
    }

    # Validate the produced target instance to guarantee correctness of the
    # reduction implementation.
    VertexCover.validate(target_instance)
    return target_instance

