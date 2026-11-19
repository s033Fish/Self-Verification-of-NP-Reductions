"""Reduction from Vertex Cover to Independent Set.

The classic reduction uses the complement of a vertex cover.  Given a graph
``G = (V, E)`` and an integer ``k`` for the *Vertex Cover* problem, we create
an *Independent Set* instance on the same graph with target size ``k' =
|V| - k``.  The following holds:

* If there exists a vertex cover ``C`` with ``|C| <= k`` then the complement
  ``V \ C`` is an independent set of size ``>= |V| - k``.
* Conversely, if there exists an independent set ``I`` with ``|I| >= |V| - k``
  then its complement ``V \ I`` is a vertex cover of size ``<= k``.

Thus the answer to the original instance is *yes* iff the answer to the
produced instance is *yes*.

The implementation validates the source instance using the ``VertexCover``
class and returns a dictionary that conforms to the ``IndependentSet``
format.  The reduction runs in linear time with respect to the size of the
input, which is polynomial.
"""

from __future__ import annotations

from typing import Dict, Any

from problems import VertexCover, IndependentSet


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance, i.e. it must have
        the keys ``"n"``, ``"edges"`` and ``"k"`` and satisfy the validation
        rules of :class:`VertexCover`.

    Returns
    -------
    dict
        A dictionary representing an Independent Set instance with the same
        vertex set and edge set, and ``k' = n - k``.
    """
    # Validate the source instance; this will raise InvalidInstance if the
    # format is wrong.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges = instance["edges"]
    k: int = instance["k"]

    # The target k is n - k (the size of the complement).  This works for any
    # integer k, including negative values; the edge‑case logic of the target
    # problem will handle them correctly.
    target_k = n - k

    reduced_instance: Dict[str, Any] = {"n": n, "edges": edges, "k": target_k}

    # Validate the produced instance against the IndependentSet definition.
    IndependentSet.validate(reduced_instance)
    return reduced_instance

