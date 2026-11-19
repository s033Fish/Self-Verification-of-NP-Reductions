"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem (HamiltonianPath) and target problem (HamiltonianCycle)
are defined in ``problems.py``.  Both use the same instance format:

    {"n": <number of vertices>, "edges": [[u, v], ...]}

Vertices are numbered 0 .. n‑1.  Edges are undirected and each unordered
pair appears at most once.

The reduction must run in polynomial time and preserve the answer: the
produced Hamiltonian‑Cycle instance is a *yes* instance exactly when the
input Hamiltonian‑Path instance is a *yes* instance.

Standard textbook reductions add a universal vertex that is adjacent to
every original vertex.  That works for graphs with at least three
vertices, but it fails for the tiny edge‑cases (n = 0, 1, 2) because the
definition of Hamiltonian‑Cycle treats graphs with ≤2 vertices as always
*no*.  To handle those cases we treat them separately and construct small
target instances whose answer matches the source answer.

Reduction strategy
-------------------
* **n = 0** – The source answer is *no*.  We return an empty graph (n = 0)
  which is also *no* for Hamiltonian‑Cycle.

* **n = 1** – The source answer is *yes*.  We return a triangle (3 vertices
  with all three edges).  A triangle always has a Hamiltonian cycle, so the
  target answer is *yes*.

* **n = 2** – The source answer is *yes* iff the single possible edge
  ``[0, 1]`` is present.  We construct a 3‑vertex graph consisting of the two
  original vertices plus a new vertex ``2``.  Edges ``[0, 2]`` and ``[1, 2]``
  are always added; the edge ``[0, 1]`` is added only when it appears in the
  source instance.  The resulting graph has a Hamiltonian cycle exactly when
  it is a triangle, i.e. when the original edge existed.

* **n ≥ 3** – We add a single new vertex ``n`` and connect it to *all* original
  vertices.  Let ``G'`` be this augmented graph.  Any Hamiltonian cycle in
  ``G'`` must use the new vertex exactly twice, linking two original vertices
  ``u`` and ``v``.  Removing the new vertex yields a Hamiltonian path from
  ``u`` to ``v`` in the original graph, and conversely any Hamiltonian path
  can be extended to a Hamiltonian cycle by inserting the new vertex between
  its endpoints.  Hence ``G'`` has a Hamiltonian cycle iff the original graph
  has a Hamiltonian path.

The implementation below follows this plan.  It does not import the heavy
``problems`` module – the reduction only needs to manipulate the instance
dictionary, which keeps the script lightweight and fast.
"""

from __future__ import annotations
from typing import List, Dict, Any


def _edge(u: int, v: int) -> List[int]:
    """Return a canonical undirected edge representation ``[u, v]``.

    The problems expect each edge to appear with ``u < v`` (the original
    generator enforces this).  This helper ensures we always emit edges in a
    consistent order.
    """
    return [u, v] if u < v else [v, u]


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        Dictionary with keys ``"n"`` (int) and ``"edges"`` (list of ``[u, v]``).

    Returns
    -------
    dict
        A new instance of the Hamiltonian‑Cycle problem preserving the answer.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Helper to build the result dict succinctly.
    def make_result(num_vertices: int, edge_list: List[List[int]]) -> Dict[str, Any]:
        return {"n": num_vertices, "edges": edge_list}

    # ----- Small‑case handling ------------------------------------------------
    if n == 0:
        # Source is always "no"; return an empty graph which is also "no".
        return make_result(0, [])

    if n == 1:
        # Source is "yes".  Return a triangle (3‑vertex complete graph).
        triangle_edges = [_edge(0, 1), _edge(1, 2), _edge(2, 0)]
        return make_result(3, triangle_edges)

    if n == 2:
        # Determine whether the original edge [0,1] exists.
        has_edge_01 = any(set(e) == {0, 1} for e in edges)
        # Build a 3‑vertex graph: vertices 0,1 (original) and 2 (new).
        edge_list: List[List[int]] = [_edge(0, 2), _edge(1, 2)]
        if has_edge_01:
            edge_list.append(_edge(0, 1))
        return make_result(3, edge_list)

    # ----- General case (n >= 3) --------------------------------------------
    new_vertex = n  # index of the added universal vertex
    result_edges: List[List[int]] = []
    # Copy original edges (ensure canonical order).
    for u, v in edges:
        result_edges.append(_edge(u, v))
    # Connect the new vertex to every original vertex.
    for v in range(n):
        result_edges.append(_edge(new_vertex, v))

    return make_result(n + 1, result_edges)

# The module's public interface is the ``reduce`` function.  Some automated
# testing harnesses import ``reduce`` directly from this file.

