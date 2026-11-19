"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem (HamiltonianCycle) expects an instance of the form

    {"n": n, "edges": [[u, v], ...]}

where the vertices are ``0 .. n-1`` and the edges are undirected.

The target problem (HamiltonianPath) uses the same representation but
interprets the instance as asking whether there exists a *path* that
visits every vertex exactly once (endpoints are unrestricted).

We construct, in polynomial time, an instance of HamiltonianPath that
has a Hamiltonian path **iff** the original graph has a Hamiltonian
cycle.  The classic reduction works as follows:

1. Pick an arbitrary vertex ``v0`` (we use ``0`` when ``n > 2``).
2. Remove ``v0`` from the graph and duplicate it into two new vertices
   ``a`` and ``b``.  Both ``a`` and ``b`` are connected to every former
   neighbour of ``v0``.
3. Attach a pendant leaf to each of ``a`` and ``b`` (vertices ``a_leaf``
   and ``b_leaf``).  These leaves have degree 1, forcing any Hamiltonian
   path to start at one leaf and end at the other.

If the original graph has a Hamiltonian cycle, we can break the cycle at
the two edges incident to ``v0`` to obtain a Hamiltonian *path* on the
remaining vertices, starting at a neighbour ``u`` and ending at a
neighbour ``w`` of ``v0``.  The constructed graph then admits the path

    a_leaf – a – u … w – b – b_leaf

which visits every vertex exactly once.  Conversely, any Hamiltonian
path in the constructed graph must start at ``a_leaf`` and end at
``b_leaf`` (the only degree‑1 vertices).  Removing those two leaves gives
us a Hamiltonian path from ``a`` to ``b`` that visits all original
vertices (except ``v0``).  The neighbours of ``a`` and ``b`` in this path
are neighbours of ``v0`` in the original graph, and adding ``v0`` back
between them yields a Hamiltonian cycle.

For trivial instances (``n <= 2``) the source problem is always a *no*
instance.  In that case we simply output a target instance with ``n = 0``
which is also a *no* instance for HamiltonianPath.

The implementation below follows this construction, performs the
necessary re‑indexing (the removed vertex is omitted), and deduplicates
edges to satisfy the format requirements.
"""

from __future__ import annotations

def reduce(instance: dict) -> dict:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance: dict
        The source instance with keys ``"n"`` and ``"edges"``.

    Returns
    -------
    dict
        A target instance for the HamiltonianPath problem.
    """

    n = instance.get("n", 0)
    edges = instance.get("edges", [])

    # Trivial cases: the source is always a NO instance.
    if n <= 2:
        # HamiltonianPath also answers NO for n = 0.
        return {"n": 0, "edges": []}

    # Choose vertex 0 as the vertex to be duplicated.
    v0 = 0

    # Determine neighbours of v0.
    neighbours = set()
    filtered_edges = []  # edges that do not involve v0
    for u, v in edges:
        if u == v0:
            neighbours.add(v)
        elif v == v0:
            neighbours.add(u)
        else:
            filtered_edges.append((u, v))

    # Re‑index vertices: we remove v0 and map the remaining old vertices
    # to a contiguous range 0 .. (n-2).
    old_to_new = {}
    new_id = 0
    for old in range(n):
        if old == v0:
            continue
        old_to_new[old] = new_id
        new_id += 1

    # IDs for the new vertices a, b, a_leaf, b_leaf.
    a = new_id
    b = new_id + 1
    a_leaf = new_id + 2
    b_leaf = new_id + 3
    new_n = new_id + 4

    # Translate the retained edges to the new indexing.
    translated_edges = []
    for u, v in filtered_edges:
        translated_edges.append([old_to_new[u], old_to_new[v]])

    # Add pendant leaves.
    translated_edges.append([a_leaf, a])
    translated_edges.append([b_leaf, b])

    # Connect a and b to every former neighbour of v0.
    for nb in neighbours:
        nb_new = old_to_new[nb]
        translated_edges.append([a, nb_new])
        translated_edges.append([b, nb_new])

    # Deduplicate edges and enforce u < v ordering as required by the
    # problem specification.
    seen = set()
    final_edges = []
    for u, v in translated_edges:
        if u == v:
            continue
        if u > v:
            u, v = v, u
        if (u, v) not in seen:
            seen.add((u, v))
            final_edges.append([u, v])

    return {"n": new_n, "edges": final_edges}

