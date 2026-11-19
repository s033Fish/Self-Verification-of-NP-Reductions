"""Reduction from Vertex Cover to Dominating Set.

The source problem is defined in :class:`problems.VertexCover` and the
target problem in :class:`problems.DominatingSet`.  Both problems use the
same graph representation – a dictionary with keys "n", "edges" and
"k", where edges is a list of undirected edges [u, v].

We implement the classic polynomial‑time reduction:

* For every edge (u, v) of the original graph we introduce a fresh
  vertex w_{uv} that is adjacent to u and v.  The original edges are kept
  unchanged.
* Isolated vertices (vertices of degree zero) pose a problem because a
  dominating set must contain them, while a vertex cover does not.  To keep
  the answers equivalent we increase the budget k by the number of isolated
  vertices.  In the reduced instance any feasible dominating set must contain
  all isolated vertices, leaving exactly k additional vertices to dominate
  the rest of the graph – these correspond to a vertex cover of the original
  instance.

The reduction runs in polynomial time and produces a valid instance of the
target problem.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance – it must pass
        ``VertexCover.validate``.

    Returns
    -------
    dict
        A dictionary representing a Dominating Set instance.  The returned
        instance satisfies ``DominatingSet.validate`` and has the property
        that the original instance is a *yes* instance iff the returned one
        is a *yes* instance.
    """

    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute degrees to find isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    # New vertices: one for each original edge.
    m = len(edges)
    new_n = n + m

    # Start with a copy of the original edges.
    new_edges: List[List[int]] = [edge[:] for edge in edges]

    # For each edge (u, v) add a new vertex w = n + i and connect it to u and v.
    for i, (u, v) in enumerate(edges):
        w = n + i
        new_edges.append([u, w])
        new_edges.append([v, w])

    # Adjust the budget: we need to allow the isolated vertices to be taken
    # into the dominating set.
    new_k = k + isolated

    reduced_instance = {"n": new_n, "edges": new_edges, "k": new_k}

    # Ensure the target instance is well‑formed.
    DominatingSet.validate(reduced_instance)
    return reduced_instance

