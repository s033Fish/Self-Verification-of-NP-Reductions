"""Reduction from Independent Set to Vertex Cover.

The classic reduction uses the complement relationship between independent
sets and vertex covers: a set S \subseteq V is an independent set in G iff its
complement V \ S is a vertex cover of G. Therefore, asking whether G has an
independent set of size at least k is equivalent to asking whether G has a
vertex cover of size at most n‑k.

The ``reduce`` function validates the source instance using the ``IndependentSet``
class from ``problems.py`` and returns a new dictionary suitable for the
``VertexCover`` class, keeping the same graph and setting ``k' = n - k``.
"""

from __future__ import annotations

from typing import Any, Dict, List

# Import the problem definitions for validation.
from problems import IndependentSet, VertexCover


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys "n", "edges" and "k" describing a
        graph and the desired independent‑set size.

    Returns
    -------
    dict
        A new instance for the Vertex Cover problem with the same graph and
        ``k' = n - k``.
    """
    # Validate the incoming Independent Set instance.  This will raise
    # ``InvalidInstance`` if the format is incorrect.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement reduction: size of a vertex cover needed is n - k.
    k_prime: int = n - k

    reduced: Dict[str, Any] = {
        "n": n,
        "edges": edges,
        "k": k_prime,
    }

    # Validate the produced target instance to ensure correctness of the
    # transformation (helps catch programming mistakes early).
    VertexCover.validate(reduced)
    return reduced

