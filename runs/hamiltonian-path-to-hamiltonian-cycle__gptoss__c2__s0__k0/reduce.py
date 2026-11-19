"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem (HamiltonianPath) asks whether an undirected graph
contains a Hamiltonian *path* (a simple path that visits every vertex
exactly once).  The target problem (HamiltonianCycle) asks whether an
undirected graph contains a Hamiltonian *cycle* (a simple cycle that
visits every vertex exactly once and returns to its start).

Standard reduction:
    Given a graph G = (V, E) with |V| = n, create a new graph G' by
    adding a fresh vertex x and connecting x to every vertex of V.
    Formally, G' has vertex set V \cup {x} and edge set E \cup
    {{v, x} : v \in V}.

    *If G has a Hamiltonian path*, say v₁‑…‑vₙ, then the cycle
    x‑v₁‑…‑vₙ‑x is a Hamiltonian cycle in G'.
    *If G' has a Hamiltonian cycle*, x must appear in the cycle (since
    it is the only vertex of degree n). Removing x leaves a Hamiltonian
    path in G between the two neighbours of x on the cycle.

Edge‑case handling:
    - n = 0: the reduction produces a single‑vertex graph, which has no
      Hamiltonian cycle, matching the source answer (no).
    - n = 1: the above construction would yield a 2‑vertex graph, and
      the target problem defines all graphs with n <= 2 as "no".  Yet a
      Hamiltonian path exists for the source.  To preserve correctness
      we map this unique yes‑instance to a trivial yes‑instance of the
      target problem – a triangle (3‑vertex complete graph).
    - n >= 2: the standard construction works and respects the answer.

The function runs in O(n + |E|) time and uses only basic Python data
structures, satisfying the polynomial‑time requirement.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n" (int) and "edges" (list of
        two‑element lists) describing an undirected graph as specified
        in ``problems.py`` for the *HamiltonianPath* problem.

    Returns
    -------
    dict
        An instance of the *HamiltonianCycle* problem that is a "yes"
        instance iff the input instance is a "yes" instance.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Special handling for the single‑vertex case.
    if n == 1:
        # Return a simple triangle which trivially has a Hamiltonian cycle.
        return {
            "n": 3,
            "edges": [[0, 1], [1, 2], [2, 0]],
        }

    # General construction: add a new vertex ``new_v`` connected to all
    # existing vertices.
    new_v = n  # the fresh vertex id
    new_n = n + 1
    # Copy original edges and add the star edges from ``new_v``.
    new_edges = [list(e) for e in edges]  # shallow copy to avoid mutation
    for v in range(n):
        new_edges.append([v, new_v])

    return {"n": new_n, "edges": new_edges}
