"""Reduction from Clique to Independent Set.

The classic polynomial‑time many‑one reduction uses the complement graph:
 a set of vertices forms a clique in G iff it forms an independent set in the
 complement of G. Therefore we keep the same vertex set and the same target
 size ``k`` and replace the edge list by the complement edge list.

The function ``reduce`` expects a valid instance of :class:`problems.Clique`
 (the source problem) and returns a valid instance of
 :class:`problems.IndependentSet` (the target problem). Validation is
 performed by the problem classes themselves – we simply construct the new
 dictionary.

The implementation runs in O(n^2) time, which is polynomial in the size of
 the input.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem definitions for validation.  The import works because
# ``problems.py`` resides in the same directory.
import problems


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is assumed to be a list of undirected edges ``[u, v]`` with
    ``u != v`` and each unordered pair appears at most once.  The complement
    contains exactly those unordered pairs that are *not* present in the
    original edge list.
    """
    # Use a set of frozensets for O(1) membership tests.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    The reduction is:
        G = (V, E), k  ->  G' = (V, E_complement), k

    The returned dictionary follows the format required by
    :class:`problems.IndependentSet`.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.
    problems.Clique.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Compute complement edges.
    comp_edges = _complement_edges(n, edges)

    target_instance = {"n": n, "edges": comp_edges, "k": k}

    # Validate the target instance before returning, to guarantee correctness
    # of the reduction implementation.
    problems.IndependentSet.validate(target_instance)
    return target_instance
