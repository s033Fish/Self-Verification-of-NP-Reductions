"""Reduction from Independent Set to Clique.

The classic polynomial‑time many‑one reduction constructs the complement of the
input graph: an independent set of size *k* in a graph *G* corresponds to a
clique of size *k* in the complement graph *G̅* (the graph on the same vertex
set where two distinct vertices are adjacent exactly when they are **not**
adjacent in *G*).

The source problem is :class:`IndependentSet` and the target problem is
``Clique`` – both are defined in ``problems.py``.  An instance of either problem
is a plain ``dict`` with the keys ``"n"``, ``"edges"`` and ``"k"``.

The ``reduce`` function validates the source instance, builds the complement
edge list (without self‑loops or duplicate edges), and returns a new instance
that satisfies the target validation rules.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import IndependentSet, Clique


def _edge_set(edges: List[List[int]]) -> set[frozenset[int]]:
    """Convert a list of ``[u, v]`` edges to a set of unordered pairs.

    The helper is used to test membership when constructing the complement.
    """
    return {frozenset((u, v)) for u, v in edges}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ``IndependentSet`` instance to a ``Clique`` instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``IndependentSet`` format.

    Returns
    -------
    dict
        An instance of the ``Clique`` problem that is a yes‑instance exactly
        when the input is a yes‑instance.
    """
    # Validate the source instance – this also checks that the required keys
    # are present and that the graph description is well‑formed.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build the complement graph.
    original_edge_set = _edge_set(original_edges)
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in original_edge_set:
                complement_edges.append([u, v])

    reduced_instance: Dict[str, Any] = {
        "n": n,
        "edges": complement_edges,
        "k": k,
    }

    # Ensure the produced instance satisfies the target validation rules.
    Clique.validate(reduced_instance)
    return reduced_instance

