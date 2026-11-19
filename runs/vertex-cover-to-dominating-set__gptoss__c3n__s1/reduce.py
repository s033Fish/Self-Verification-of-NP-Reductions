"""Reduction from Vertex Cover to Dominating Set.

The source problem is :class:`VertexCover` defined in ``problems.py``.
The target problem is :class:`DominatingSet` defined in the same file.

Given an instance ``I = {"n": n, "edges": [[u, v], ...], "k": k}`` of
Vertex Cover, we construct an instance ``I'`` of Dominating Set such that
``I`` is a *yes*-instance iff ``I'`` is a *yes*-instance.

Construction (standard textbook reduction):

* For every edge ``(u, v)`` of the original graph we introduce a new
  vertex ``w`` (unique for that edge) and connect it to ``u`` and ``v``.
  The original edges are kept unchanged – they are useful for domination
  of the original vertices but are not required for the correctness of the
  reduction.
* Let ``iso`` be the set of isolated vertices of the original graph (those
  with degree zero).  An isolated vertex cannot be dominated by any other
  vertex, therefore any dominating set must contain the isolated vertex
  itself.  Consequently we increase the budget by ``|iso|``.
* The new instance is ``{"n": n', "edges": E', "k": k'}`` where
  ``n' = n + |E|`` (one fresh vertex per original edge) and ``k' = k + |iso|``.

Correctness sketch:

* (→) If ``C`` is a vertex cover of size ≤ ``k``, let ``D = C ∪ iso``.
  ``D`` has size ≤ ``k'`` and dominates the whole new graph: original
  vertices not in ``C`` are adjacent to a vertex of ``C`` (otherwise the
  incident edge would be uncovered), edge‑vertices are adjacent to an
  endpoint in ``C``, and isolated vertices dominate themselves.
* (←) Let ``D`` be a dominating set of size ≤ ``k'``.  All isolated
  vertices must belong to ``D``; remove them, obtaining ``D'`` of size ≤ ``k``.
  If ``D'`` contains any edge‑vertex ``w_{uv}``, replace it by one of its
  neighbours ``u`` or ``v`` – the size does not increase and domination is
  preserved.  After this replacement ``D'`` consists only of original
  vertices and dominates every edge‑vertex, which means for each original
  edge at least one endpoint lies in ``D'``.  Hence ``D'`` is a vertex cover
  of size ≤ ``k``.

The implementation below follows this construction.  It also handles the
trivial case ``k < 0`` by returning a guaranteed‑no instance of Dominating
Set (negative ``k`` is always a no‑instance for both problems).
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance as described in
        ``problems.py``.

    Returns
    -------
    dict
        A Dominating Set instance that is equivalent with respect to the
        yes/no answer.
    """
    # Validate the source instance first – will raise InvalidInstance if bad.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # If k is negative, the source answer is always NO.  Return a guaranteed
    # NO instance for the target as well (negative k).
    if k < 0:
        return {"n": 0, "edges": [], "k": -1}

    # Compute degree to find isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated_count = sum(1 for d in degree if d == 0)

    # Build the new graph.
    new_edges: List[List[int]] = []
    # Keep original edges – they help dominate original vertices.
    new_edges.extend([list(e) for e in edges])

    new_n = n
    for u, v in edges:
        # Introduce a fresh vertex for this edge.
        w = new_n
        new_n += 1
        new_edges.append([u, w])
        new_edges.append([v, w])

    new_k = k + isolated_count

    new_instance = {"n": new_n, "edges": new_edges, "k": new_k}
    # Validate the target instance (optional, but catches bugs early).
    DominatingSet.validate(new_instance)
    return new_instance

