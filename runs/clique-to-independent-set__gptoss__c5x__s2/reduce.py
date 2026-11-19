"""Reduction from Clique to Independent Set.

The source problem is :class:`Clique` (defined in ``problems.py``) and the
target problem is :class:`IndependentSet`.  Both problems use the same graph
representation – a dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` –
where ``edges`` is a list of undirected edges ``[u, v]`` with ``0 <= u, v < n``.

The classic polynomial‑time reduction is to take the complement of the input
graph.  A set of vertices forms a clique in ``G`` iff it is an independent set
in the complement ``\overline{G}``.

The ``reduce`` function validates the source instance using ``Clique.validate``
and then constructs the complement graph.  The returned instance has the same
``n`` and ``k`` values; the edge list consists of all unordered vertex pairs
that are *not* edges of the original graph.

The implementation runs in ``O(n^2)`` time and uses only standard Python data
structures, satisfying the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set, Tuple

from problems import Clique, IndependentSet


def _edge_key(u: int, v: int) -> Tuple[int, int]:
    """Return a canonical representation of an undirected edge.

    The validation in ``problems.py`` guarantees ``u != v`` and that each edge
    appears only once, but using a sorted tuple makes set operations easy.
    """

    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Clique instance (see ``Clique`` docstring).

    Returns
    -------
    dict
        An Independent Set instance that is a *yes* instance exactly when the
        input is a *yes* instance.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # format is incorrect.
    Clique.validate(instance)

    n: int = instance["n"]
    k: int = instance["k"]
    original_edges: List[List[int]] = instance["edges"]

    # Build a set of all edges present in the original graph for O(1) look‑up.
    present: Set[Tuple[int, int]] = set()
    for u, v in original_edges:
        present.add(_edge_key(u, v))

    # Construct the complement edge list.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    # The target instance uses the same ``n`` and ``k`` values.
    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": complement_edges,
        "k": k,
    }

    # Validate the produced instance for sanity – this also serves as a guard
    # against accidental format mistakes.
    IndependentSet.validate(target_instance)

    return target_instance

