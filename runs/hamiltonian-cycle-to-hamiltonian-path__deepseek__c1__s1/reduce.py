"""Polynomial-time reduction from Hamiltonian Cycle to Hamiltonian Path.

Idea
----
Fix a vertex ``v`` of the source graph ``G`` (we use ``v = 0``).  In any
Hamiltonian cycle of ``G`` the vertex ``v`` has exactly two neighbours on the
cycle, say ``a`` and ``b``; deleting ``v`` from the cycle leaves a Hamiltonian
path of ``G - v`` running from ``a`` to ``b``.  Conversely, if ``G - v`` has a
Hamiltonian path whose two endpoints are both neighbours of ``v``, then adding
``v`` closes that path into a Hamiltonian cycle.

So we must build a graph ``H`` that has a Hamiltonian path iff ``G - v`` has a
Hamiltonian path whose endpoints both lie in ``N(v)``.

Construction (for ``n >= 3``)
-----------------------------
Keep every vertex of ``G`` except ``v`` (relabelled to ``0 .. n-2``) and add
four new vertices ``x, y, z, w``:

* ``x`` is adjacent to every vertex of ``N(v)`` and to ``y``;
* ``z`` is adjacent to every vertex of ``N(v)`` and to ``w``;
* the edges among ``V \\ {v}`` are exactly the edges of ``G``;
* ``y`` and ``w`` are leaves, so in every Hamiltonian path of ``H`` they are
  the two endpoints and the path is forced to look like

      y - x - p_1 - p_2 - ... - p_{n-1} - z - w

  with ``{p_i} = V \\ {v}``.  Because ``x`` only reaches ``N(v)`` and ``z``
  only reaches ``N(v)``, both ``p_1`` and ``p_{n-1}`` lie in ``N(v)`` and
  ``p_1 ... p_{n-1}`` is a Hamiltonian path of ``G - v``.  Adding ``v`` closes
  it into a Hamiltonian cycle of ``G``.

The construction uses ``O(n + m)`` time and space.  For ``n <= 2`` the source
is always a "no" instance, so we return the always-"no" target instance
``{"n": 0, "edges": []}``.
"""


def reduce(instance):
    """Reduce a Hamiltonian Cycle instance to a Hamiltonian Path instance."""
    n = instance["n"]
    edges = instance["edges"]

    # Hamiltonian Cycle is always "no" for n <= 2 (a simple cycle needs >= 3
    # vertices); return an always-"no" Hamiltonian Path instance.
    if n < 3:
        return {"n": 0, "edges": []}

    v = 0
    rest = [u for u in range(n) if u != v]
    mapping = {u: i for i, u in enumerate(rest)}

    # Adjacency of the source graph, to know N(v).
    neighbours_of_v = set()
    for a, b in edges:
        if a == v:
            neighbours_of_v.add(b)
        elif b == v:
            neighbours_of_v.add(a)

    # New vertex labels: x, y, z, w.
    x = n - 1
    y = n
    z = n + 1
    w = n + 2

    new_edges = []

    # Edges of G that do not touch v, relabelled.
    for a, b in edges:
        if a == v or b == v:
            continue
        new_edges.append([mapping[a], mapping[b]])

    # x and z are each joined to every neighbour of v.
    for u in rest:
        if u in neighbours_of_v:
            new_edges.append([mapping[u], x])
            new_edges.append([mapping[u], z])

    # The two leaves that force the endpoints of the path.
    new_edges.append([x, y])
    new_edges.append([z, w])

    return {"n": n + 3, "edges": new_edges}
