"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction
------------
Given a Hamiltonian Path instance G = (V, E) with n = |V| vertices:

* If n <= 1 we handle the degenerate cases directly, because the standard
  gadget needs at least two original vertices to form a cycle:
    - n = 0: Hamiltonian Path is NO.  Return the empty graph (n' = 0),
      which has no Hamiltonian cycle.
    - n = 1: Hamiltonian Path is YES (single vertex).  Return the
      triangle on 3 vertices, which has a Hamiltonian cycle.
* If n >= 2: add one new vertex w = n and connect it to every vertex of G:

      G' = ({0, ..., n}, E ∪ {{i, w} : 0 <= i < n})

  Claim: G has a Hamiltonian path  <=>  G' has a Hamiltonian cycle.

  (=>) Let v_0, v_1, ..., v_{n-1} be a Hamiltonian path of G.  Then
       w, v_0, v_1, ..., v_{n-1}, w is a Hamiltonian cycle of G'.
  (<=) Any Hamiltonian cycle of G' visits w exactly once, so it uses
       exactly two edges incident to w, say {w, a} and {w, b}.  Removing w
       from the cycle leaves a Hamiltonian path of G with endpoints a, b.

The construction is clearly polynomial time (O(n) new vertices/edges) and
does not call any brute-force solver.
"""

from __future__ import annotations

from typing import Any


def _triangle() -> dict[str, Any]:
    return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    if n <= 1:
        # n = 0 -> NO  (empty graph, no cycle)
        # n = 1 -> YES (triangle has a Hamiltonian cycle)
        return {"n": 0, "edges": []} if n == 0 else _triangle()

    w = n
    new_edges = [list(e) for e in edges]
    new_edges.extend([i, w] for i in range(n))
    return {"n": n + 1, "edges": new_edges}
