"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Given a source instance G = (V, E) with V = {0, ..., n-1}:

* If n <= 2, G has no Hamiltonian cycle.  Return the target instance
  {"n": 0, "edges": []}, which has no Hamiltonian path.

* Otherwise fix the vertex v = 0.  Build the target graph H on n + 3
  vertices:

      - every vertex u in V \\ {v} becomes a vertex of H;
      - add two copies v1, v2 of v, each adjacent to exactly the
        neighbours of v (in V \\ {v});
      - add a private leaf l1 attached to v1 and a private leaf l2
        attached to v2.

  H has a Hamiltonian path iff G has a Hamiltonian cycle:

  (<=) A cycle v, a1, ..., a_{n-1}, v in G gives the Hamiltonian path
       l1 - v1 - a1 - ... - a_{n-1} - v2 - l2 in H.

  (=>) l1 and l2 have degree one, so in any Hamiltonian path of H they
       are the two endpoints.  The path is therefore
       l1 - v1 - a1 - ... - a_{n-1} - v2 - l2, where a1, ..., a_{n-1}
       is a permutation of V \\ {v}; a1 and a_{n-1} are neighbours of v,
       so v, a1, ..., a_{n-1}, v is a Hamiltonian cycle of G.

The construction is clearly polynomial: it copies each edge once and adds
O(n) new edges.
"""

from __future__ import annotations


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    if n <= 2:
        # Source answer is always "no"; return a target instance that is
        # also always "no".
        return {"n": 0, "edges": []}

    # New labels:
    #   original u (u != 0) -> u - 1          (0 .. n-2)
    #   v1 -> n - 1, v2 -> n
    #   leaf1 -> n + 1, leaf2 -> n + 2
    v1 = n - 1
    v2 = n
    leaf1 = n + 1
    leaf2 = n + 2

    new_edges = []
    seen = set()

    def add(a, b):
        if a > b:
            a, b = b, a
        key = (a, b)
        if key not in seen:
            seen.add(key)
            new_edges.append([a, b])

    neighbors_of_v = set()
    for u, w in edges:
        if u == 0:
            neighbors_of_v.add(w)
        elif w == 0:
            neighbors_of_v.add(u)
        else:
            add(u - 1, w - 1)

    for u in neighbors_of_v:
        add(u - 1, v1)
        add(u - 1, v2)

    add(v1, leaf1)
    add(v2, leaf2)

    return {"n": n + 3, "edges": new_edges}
