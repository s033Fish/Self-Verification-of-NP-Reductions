"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem is :class:`HamiltonianPath` (undirected graph, any
endpoints).  The target problem is :class:`HamiltonianCycle` (undirected
graph, must form a cycle that visits every vertex exactly once).

For graphs with at least three vertices we use the classic reduction:

* Add a new vertex ``s`` (index ``n``) to the graph.
* Connect ``s`` to **all** original vertices.

If the original graph has a Hamiltonian path, then by connecting the two
endpoints of that path to ``s`` we obtain a Hamiltonian cycle in the new
graph.  Conversely, any Hamiltonian cycle in the new graph must contain
``s`` exactly once, and removing ``s`` yields a Hamiltonian path in the
original graph.

The reduction must also be correct for the small edge‑case values of ``n``
handled by the problem definitions:

* ``n = 0`` – source answer is ``no``.  We output an empty graph (``n = 0``)
  which is also a ``no`` instance for Hamiltonian Cycle.
* ``n = 1`` – source answer is ``yes``.  No Hamiltonian cycle exists on a
  single vertex, so we output a *fixed* positive instance: the triangle
  graph on three vertices, which trivially has a Hamiltonian cycle.
* ``n = 2`` – source answer is ``yes`` iff the single possible edge ``[0,
  1]`` is present.  We again compute the source answer directly and
  output either the triangle (for ``yes``) or the empty graph (for ``no``).

All other instances (``n >= 3``) are transformed by the generic gadget
described above.  The transformation runs in linear time in the size of
the input graph, satisfying the polynomial‑time requirement.
"""

from __future__ import annotations

from typing import Dict, List

from problems import HamiltonianPath, HamiltonianCycle


def _source_answer_is_yes(instance: Dict) -> bool:
    """Determine the answer for a Hamiltonian‑Path instance.

    The instance size is at most 2 in the contexts where this helper is
    used, so a direct case analysis is sufficient and runs in constant
    time.
    """
    n: int = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        # There is at most one edge [0,1].  The answer is yes iff that edge
        # exists.
        for u, v in instance["edges"]:
            if {u, v} == {0, 1}:
                return True
        return False
    # For n >= 3 we never call this helper.
    raise AssertionError("_source_answer_is_yes called with n >= 3")


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dict adhering to the format of :class:`HamiltonianPath`.

    Returns
    -------
    dict
        An instance of :class:`HamiltonianCycle` whose answer matches the
        answer of ``instance``.
    """
    # Validate source instance (may raise InvalidInstance).
    HamiltonianPath.validate(instance)

    n: int = instance["n"]

    # Small‑size special handling.
    if n <= 2:
        yes = _source_answer_is_yes(instance)
        if yes:
            # Return a fixed positive instance: a triangle (3‑vertex clique).
            return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}
        else:
            # Return a fixed negative instance: empty graph (n = 0).
            return {"n": 0, "edges": []}

    # General case n >= 3.
    new_n = n + 1
    new_edges: List[List[int]] = []
    # Keep original edges.
    for edge in instance["edges"]:
        new_edges.append([edge[0], edge[1]])
    # Connect the new vertex (index n) to every original vertex.
    for v in range(n):
        new_edges.append([v, n])

    reduced_instance = {"n": new_n, "edges": new_edges}
    # Validate target instance before returning.
    HamiltonianCycle.validate(reduced_instance)
    return reduced_instance

