"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Reduction idea
--------------
Given an undirected graph G = (V, E) with n = |V| vertices, an instance of
Hamiltonian Cycle:

* If n <= 2, G can never have a Hamiltonian cycle, so we return a target
  instance that is always a "no" (the empty graph with n = 0).

* Otherwise pick a vertex v (we use v = 0) and build G' as follows:
    - keep every vertex of V \\ {v};
    - replace v by two new vertices v' and v'';
    - for every edge {v, w} of G add the edges {v', w} and {v'', w};
    - add two new pendant vertices p' and p'' with edges {p', v'} and
      {p'', v''};
    - keep all edges of G that do not touch v.

  p' and p'' have degree one, so in any Hamiltonian path of G' they must be
  the two endpoints.  Hence the path has the form

      p' - v' - a1 - a2 - ... - a_{n-1} - v'' - p''

  where a1..a_{n-1} are exactly the vertices of V \\ {v}.  Because v' and v''
  are only adjacent to neighbours of v, a1 and a_{n-1} are neighbours of v,
  so

      v - a1 - a2 - ... - a_{n-1} - v

  is a Hamiltonian cycle of G.  Conversely a Hamiltonian cycle of G through v
  gives such a path.  For n >= 3 the two endpoints a1 and a_{n-1} are
  distinct, so the cycle is a genuine simple cycle.

The construction uses O(n + m) time and space, hence is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Hamiltonian Cycle instance to a Hamiltonian Path instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: the source is always "no"; return an always-"no" target.
    if n <= 2:
        return {"n": 0, "edges": []}

    # Relabel V \ {0} as 0 .. n-2.
    # New vertices: v' = n-1, v'' = n, p' = n+1, p'' = n+2.
    v_prime = n - 1
    v_double_prime = n
    p_prime = n + 1
    p_double_prime = n + 2

    new_edges: list[list[int]] = []

    for edge in edges:
        a, b = edge
        if a == 0:
            # edge {0, b} -> {v', b-1} and {v'', b-1}
            w = b - 1
            new_edges.append([v_prime, w])
            new_edges.append([v_double_prime, w])
        elif b == 0:
            # edge {a, 0} -> {v', a-1} and {v'', a-1}
            w = a - 1
            new_edges.append([v_prime, w])
            new_edges.append([v_double_prime, w])
        else:
            # edge inside V \ {0}: relabel both endpoints
            new_edges.append([a - 1, b - 1])

    # Pendant vertices force v' and v'' to be the path endpoints.
    new_edges.append([p_prime, v_prime])
    new_edges.append([p_double_prime, v_double_prime])

    return {"n": n + 3, "edges": new_edges}
