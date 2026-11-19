"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Given an undirected graph G = (V, E) with n = |V| >= 3, pick a vertex v
(we use v = 0).  Build G' as follows:

  * keep every vertex u != v, relabelled to 0..n-2;
  * replace v by two new vertices v1 and v2, each adjacent to exactly the
    neighbours of v in G (i.e. for every edge {v, u} of G add {v1, u} and
    {v2, u});
  * add two new leaves s and t with edges {s, v1} and {t, v2}.

Claim: G has a Hamiltonian cycle iff G' has a Hamiltonian path.

(=>) If v - a1 - a2 - ... - a_{n-1} - v is a Hamiltonian cycle of G, then
     s - v1 - a1 - a2 - ... - a_{n-1} - v2 - t is a Hamiltonian path of G'.

(<=) s and t have degree 1, so in any Hamiltonian path of G' they must be
     the two endpoints.  The path therefore has the form
     s - v1 - a1 - ... - a_{n-1} - v2 - t, and merging v1, v2 back into v
     yields the Hamiltonian cycle v - a1 - ... - a_{n-1} - v of G.

For n <= 2 the source instance is always a NO instance (a simple graph needs
at least 3 vertices for a cycle), so we return the trivially NO target
instance {"n": 0, "edges": []}.

The reduction clearly runs in O(n + m) time.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: Hamiltonian Cycle is always NO.  Return a NO Hamiltonian Path
    # instance (n = 0 is documented as NO).
    if n <= 2:
        return {"n": 0, "edges": []}

    # Relabelling: old vertex u (1 <= u <= n-1) -> u - 1.
    # New vertices: v1 = n-1, v2 = n, s = n+1, t = n+2.
    v1 = n - 1
    v2 = n
    s = n + 1
    t = n + 2

    new_edges: list[list[int]] = []
    seen: set[tuple[int, int]] = set()

    def add(a: int, b: int) -> None:
        if a > b:
            a, b = b, a
        key = (a, b)
        if key not in seen:
            seen.add(key)
            new_edges.append([a, b])

    for u, w in edges:
        if u == 0:
            add(v1, w - 1)
            add(v2, w - 1)
        elif w == 0:
            add(v1, u - 1)
            add(v2, u - 1)
        else:
            add(u - 1, w - 1)

    add(s, v1)
    add(t, v2)

    return {"n": n + 3, "edges": new_edges}
