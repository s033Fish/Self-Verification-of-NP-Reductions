"""Reduction from Vertex Cover to Independent Set.

The reduction is classic: a set C of vertices is a vertex cover of G iff its
complement V\C is an independent set of G. Therefore, a Vertex Cover instance
with bound ``k`` is transformed into an Independent Set instance with bound
``n - k`` on the *same* graph.

The function ``reduce`` takes a VertexCover instance (a ``dict`` with keys
``"n"``, ``"edges"`` and ``"k"``) and returns an IndependentSet instance (a
``dict`` with the same ``"n"`` and ``"edges"`` and a new ``"k"`` equal to
``n - k``).

The transformation runs in linear time in the size of the input and preserves
the answer: the original instance is a *yes* instance iff the returned
instance is a *yes* instance.
"""

from __future__ import annotations

from typing import Dict, List

# Import the problem classes only for type checking / validation purposes.
from problems import VertexCover, IndependentSet, InvalidInstance


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance. It must contain the
        keys ``"n"``, ``"edges"`` and ``"k"`` and satisfy ``VertexCover.validate``.

    Returns
    -------
    dict
        An Independent Set instance with the same graph and ``k' = n - k``.
    """
    # Validate the source instance. If it is malformed we raise the same
    # ``InvalidInstance`` exception that the problem class would raise.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute the new bound for Independent Set.
    new_k = n - k

    # Construct the target instance. The graph is unchanged.
    reduced_instance = {"n": n, "edges": edges, "k": new_k}

    # Validate the target instance to ensure we produce a well‑formed one.
    IndependentSet.validate(reduced_instance)

    return reduced_instance

