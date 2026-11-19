"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem is :class:`HamiltonianPath` (undirected, any endpoints).
The target problem is :class:`HamiltonianCycle` (undirected).

For an input graph G = (V, E) we construct a new graph G' = (V', E') as
follows:

* If |V| = 0, we output a single isolated vertex.  Hamiltonian Cycle on a
  graph with ≤2 vertices is always *no*, matching the source answer.
* If |V| = 1, the source instance is always *yes*.  Since a Hamiltonian
  cycle cannot exist on ≤2 vertices, we instead output a fixed triangle
  (three vertices forming a cycle).  This instance is always *yes*.
* If |V| = 2, let the original vertices be 0 and 1 and let ``e`` be the
  presence of the edge [0, 1] in the source.  We create a third vertex 2
  and add edges (0,2) and (1,2).  If ``e`` is present we also add (0,1),
  yielding a triangle exactly when the original graph had the edge.  A
  triangle has a Hamiltonian cycle, otherwise the three‑vertex graph is a
  path and has none.  Hence the answer matches the source.
* For |V| ≥ 3 we add a new universal vertex ``u = |V|`` and connect it to
  every original vertex.  G has a Hamiltonian path iff G' has a Hamiltonian
  cycle: any Hamiltonian cycle in G' must use two edges incident to ``u``;
  removing ``u`` yields a Hamiltonian path in G, and conversely a Hamiltonian
  path in G can be closed into a cycle by inserting ``u`` at its ends.

The construction runs in O(|V| + |E|) time, i.e. polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import HamiltonianPath, HamiltonianCycle


def _edge(u: int, v: int) -> List[int]:
    """Return a canonical undirected edge representation.

    The problem format expects a list ``[u, v]`` where the order does not
    matter, but we keep the original order for consistency.
    """

    return [u, v]


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Hamiltonian‑Path instance as defined in
        ``problems.py``.

    Returns
    -------
    dict
        A dictionary representing a Hamiltonian‑Cycle instance that is a
        *yes* instance exactly when the input instance is a *yes* instance.
    """

    # Validate the source instance – this will raise InvalidInstance on error.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    orig_edges: List[List[int]] = instance["edges"]
    # Store edges as a set of frozensets for O(1) membership tests.
    edge_set = {frozenset(e) for e in orig_edges}

    # Small‑size handling according to the analysis above.
    if n == 0:
        # No vertices → answer is NO.  Return a graph with a single vertex.
        return {"n": 1, "edges": []}

    if n == 1:
        # Source is always YES.  Return a triangle which always has a Hamiltonian cycle.
        return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}

    if n == 2:
        # Determine whether the original edge (0,1) exists.
        has_edge = frozenset((0, 1)) in edge_set
        edges: List[List[int]] = [_edge(0, 2), _edge(1, 2)]
        if has_edge:
            edges.append(_edge(0, 1))
        return {"n": 3, "edges": edges}

    # General case: n >= 3.
    new_vertex = n
    edges: List[List[int]] = list(orig_edges)  # copy original edges
    # Connect the new universal vertex to every original vertex.
    for v in range(n):
        edges.append(_edge(v, new_vertex))
    return {"n": n + 1, "edges": edges}

