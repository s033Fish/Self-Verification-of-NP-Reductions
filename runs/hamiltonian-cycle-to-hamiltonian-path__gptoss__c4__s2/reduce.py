"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction (two copies with forced endpoints):
* For each original vertex v (0 ≤ v < n) create two copies:
    v_A = v            (in the first copy)
    v_B = v + n        (in the second copy)
  Preserve all original edges inside each copy.
* Add a bridge edge between vertex 0_A (0) and 0_B (n).
* Add a new leaf start vertex s = 2n and a new leaf end vertex t = 2n+1.
  Connect s to 0_A and t to 0_B.

The resulting graph has 2n+2 vertices.
If G has a Hamiltonian cycle, we can start at s, follow the cycle in the first copy
starting at 0, cross the bridge to the second copy, traverse the same cycle there,
and finish at t, yielding a Hamiltonian path.
Conversely, any Hamiltonian path must start at the unique degree‑1 vertex s and end
at the unique degree‑1 vertex t, thus it must use the bridge edge (0, n) exactly once.
Removing s, t, and the bridge leaves two Hamiltonian paths covering each copy,
which together form a Hamiltonian cycle in the original graph.

For source instances with n ≤ 2 the answer is always NO, so we map them to a trivial
NO‑instance of the target problem (the empty graph with n = 0).
"""

from __future__ import annotations

from typing import Dict, List

from problems import HamiltonianCycle, HamiltonianPath


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian Cycle instance to a Hamiltonian Path instance.

    The returned instance is a YES‑instance iff the input instance is a YES‑instance.
    """
    # Validate the source instance.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial cases: n <= 2 never have a Hamiltonian cycle.
    if n <= 2:
        target = {"n": 0, "edges": []}
        HamiltonianPath.validate(target)
        return target

    # Build the doubled graph with bridge and leaves.
    new_n = 2 * n + 2  # vertices 0..2n+1
    new_edges: List[List[int]] = []

    # Preserve edges inside each copy.
    for u, v in edges:
        new_edges.append([u, v])          # copy A
        new_edges.append([u + n, v + n])  # copy B

    # Bridge edge between 0_A and 0_B.
    new_edges.append([0, n])

    s = 2 * n      # start leaf
    t = 2 * n + 1  # end leaf
    # Connect leaves.
    new_edges.append([s, 0])  # s--0_A
    new_edges.append([n, t])  # 0_B--t

    target = {"n": new_n, "edges": new_edges}
    HamiltonianPath.validate(target)
    return target

