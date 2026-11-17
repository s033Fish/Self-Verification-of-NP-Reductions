"""Reduction from Clique to Independent Set.

The source problem is ``Clique`` (find a clique of size at least ``k``) and the
target problem is ``IndependentSet`` (find an independent set of size at least
``k``).  The classic polynomial‑time reduction is to take the complement of the
input graph: a set of vertices forms a clique in the original graph iff it is
an independent set in the complement.

Both problems use the same instance representation:

    {"n": int, "edges": [[u, v], ...], "k": int}

where ``edges`` is an undirected simple edge list (no self‑loops, no duplicate
edges).  The reduction therefore keeps ``n`` and ``k`` unchanged and replaces
``edges`` with the list of all non‑edges of the original graph.

The implementation validates the input using ``Clique.validate`` (so that any
malformed instance raises ``InvalidInstance``) and then constructs the
complement edge list in O(n²) time, which is polynomial in the size of the
instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse their validation logic.  The classes are
# defined in ``problems.py`` which lives in the same directory.
from problems import Clique, IndependentSet


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph on ``n`` vertices.

    ``edges`` is assumed to be a valid edge list for a simple undirected graph.
    The complement contains exactly those unordered pairs ``{u, v}`` with
    ``0 <= u < v < n`` that are *not* present in ``edges``.
    """
    # Build a set of frozensets for O(1) membership checks.
    existing = {frozenset((u, v)) for u, v in (e for e in edges)}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    The returned instance has the same ``n`` and ``k`` and its ``edges`` field
    describes the complement graph.  The reduction runs in polynomial time and
    preserves the answer:

    * If the original graph has a clique of size ≥ k, the complement has an
      independent set of size ≥ k.
    * Conversely, any independent set of size ≥ k in the complement corresponds
      to a clique of the same size in the original graph.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is incorrect.
    Clique.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Construct the complement edge list.
    comp_edges = _complement_edges(n, edges)

    # Build the target instance.  IndependentSet.validate will accept this
    # because it follows the same schema.
    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": comp_edges,
        "k": k,
    }

    # Optional sanity check – ensure the produced instance is valid for the
    # target problem.  This is cheap and helps catch programming errors.
    IndependentSet.validate(target_instance)

    return target_instance

