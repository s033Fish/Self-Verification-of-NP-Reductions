"""Reduction from Independent Set to Vertex Cover.

The reduction is the classic complement relationship:
For a graph G = (V, E) and an integer k, there is an independent set of
size at least k *iff* there is a vertex cover of size at most |V| - k.

Given an instance of :class:`IndependentSet` we produce an instance of
``VertexCover`` with the same vertex set and edge list, but with the
parameter ``k' = n - k``.

The function validates the source instance using the problem's validation
method and returns a dictionary that conforms to the target problem's
format.  The transformation runs in linear time in the size of the input
graph, which is polynomial.
"""

from __future__ import annotations

from typing import Dict, List, Any

from problems import IndependentSet, VertexCover, InvalidInstance


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary representing an Independent Set instance as defined in
        ``problems.py``.  It must contain the keys ``"n"``, ``"edges"`` and
        ``"k"``.

    Returns
    -------
    dict
        A Vertex Cover instance with the same ``n`` and ``edges`` and with
        ``k' = n - k``.

    Raises
    ------
    InvalidInstance
        If the input does not satisfy the Independent Set specification.
    """

    # Validate the source instance – this will raise InvalidInstance on error.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    k: int = instance["k"]
    edges: List[List[int]] = instance["edges"]

    # Compute the complement parameter for vertex cover.
    # The relationship holds for any integer k, including negative or > n.
    # The edge cases of the target problem are handled automatically because
    # VertexCover.validate will be called by any consumer if needed.
    k_prime = n - k

    # Build the target instance.  The graph structure is unchanged.
    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": edges.copy(),  # shallow copy is sufficient (list of ints)
        "k": k_prime,
    }

    # Optionally validate the produced instance against the target problem.
    # This is not strictly required for the reduction, but it helps catch
    # accidental mistakes during development.
    VertexCover.validate(target_instance)

    return target_instance

