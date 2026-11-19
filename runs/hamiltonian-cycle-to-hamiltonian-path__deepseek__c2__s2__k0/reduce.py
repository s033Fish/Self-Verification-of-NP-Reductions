"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Construction
------------
Given an undirected graph G = (V, E) with |V| = n >= 3, pick a vertex v
(here v = 0) and build a graph G' as follows:

  * replace v by two copies v' and v'';
  * for every edge {v, u} of G add the edges {v', u} and {v'', u};
  * keep every edge of G whose both endpoints differ from v;
  * add two fresh vertices a and b with the single edges {a, v'} and {b, v''}.

Claim: G has a Hamiltonian cycle  <=>  G' has a Hamiltonian path.

(=>) A Hamiltonian cycle of G enters/leaves v through two distinct
neighbours u1, u2.  The path  a - v' - u1 - ... - u2 - v'' - b  is a
Hamiltonian path of G'.

(<=) In G' the vertices a and b have degree 1, so in any Hamiltonian path
they must be the two endpoints, adjacent to v' and v'' respectively.  The
path therefore looks like  a - v' - (all other vertices) - v'' - b.
Contracting v' and v'' back into v turns it into a Hamiltonian cycle of G.

For n <= 2 the source is always a "no" instance; we return the empty
graph (n = 0), which is also a "no" instance of the target.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # n <= 2: Hamiltonian Cycle is always false.  n = 0 is a "no" instance
    # of Hamiltonian Path as well.
    if n <= 2:
        return {"n": 0, "edges": []}

    v = 0  # the vertex that gets split

    # Relabel the vertices other than v to 0 .. n-2.
    others = [u for u in range(n) if u != v]
    label = {u: i for i, u in enumerate(others)}

    v_prime = n - 1      # first copy of v
    v_double = n         # second copy of v
    a = n + 1            # pendant attached to v'
    b = n + 2            # pendant attached to v''

    new_edges = []
    seen = set()

    def add(x, y):
        if x == y:
            return
        key = (x, y) if x < y else (y, x)
        if key in seen:
            return
        seen.add(key)
        new_edges.append([key[0], key[1]])

    for e in edges:
        x, y = e[0], e[1]
        if x == v:
            u = label[y]
            add(v_prime, u)
            add(v_double, u)
        elif y == v:
            u = label[x]
            add(v_prime, u)
            add(v_double, u)
        else:
            add(label[x], label[y])

    add(a, v_prime)
    add(b, v_double)

    return {"n": n + 3, "edges": new_edges}
