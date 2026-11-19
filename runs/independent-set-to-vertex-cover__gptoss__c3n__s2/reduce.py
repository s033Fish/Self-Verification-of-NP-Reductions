"""Reduction from Independent Set to Vertex Cover.

The classic reduction uses the complement relationship between independent
sets and vertex covers: a set S is independent in G iff V\S is a vertex
cover of G. Therefore an instance (G, k) of Independent Set is a *yes*
instance iff the instance (G, n‑k) of Vertex Cover is a *yes* instance,
where n = |V|.

This file defines a single function ``reduce`` that takes a source
instance (as defined by :class:`IndependentSet`) and returns a target
instance (as defined by :class:`VertexCover`). The function validates the
input using the problem's ``validate`` method and constructs the output
dictionary with the same vertices and edges but with the transformed
parameter ``k' = n - k``.

The transformation runs in linear time with respect to the size of the
input graph, satisfying the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List

from problems import IndependentSet, VertexCover


def reduce(instance: Dict) -> Dict:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` that
        satisfies :class:`IndependentSet` validation.

    Returns
    -------
    dict
        A dictionary suitable for :class:`VertexCover`. It contains the
        same ``"n"`` and ``"edges"`` as the input and a new ``"k"`` equal to
        ``n - k_input``.
    """
    # Validate the source instance – will raise InvalidInstance on malformed
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k_input: int = instance["k"]

    # Complement transformation
    k_target = n - k_input

    # Build the target instance. The graph structure is unchanged.
    target_instance = {"n": n, "edges": edges, "k": k_target}

    # Validate the constructed target instance for safety (optional but
    # helpful during development). It will raise if we made a mistake.
    VertexCover.validate(target_instance)

    return target_instance

