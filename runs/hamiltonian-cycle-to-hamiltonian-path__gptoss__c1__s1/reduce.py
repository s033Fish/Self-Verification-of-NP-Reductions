"""Reduction from Hamiltonian Cycle (undirected) to Hamiltonian Path.

The source problem instance is a dictionary:
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1 and edges are undirected.

The target problem (Hamiltonian Path) expects the same format.

Reduction construction:
For a graph G with n >= 3 vertices, pick vertex 0 as the distinguished
vertex. Remove vertex 0 and its incident edges. Introduce two new
vertices s and t. Connect s and t to every former neighbor of 0. The
resulting graph G' has (n-1)+2 = n+1 vertices.

Claim: G has a Hamiltonian cycle iff G' has a Hamiltonian path.
Proof sketch: A Hamiltonian cycle in G visits 0 with two incident edges
    (0, u) and (0, v). Deleting 0 leaves a Hamiltonian path from u to v
    covering the remaining vertices. Adding s--u and t--v yields a
    Hamiltonian path from s to t in G'. Conversely, any Hamiltonian path
    in G' must start at s and end at t (they have degree equal to the
    number of neighbors of 0). Removing s and t restores a Hamiltonian
    path between two neighbors of 0, which together with vertex 0 and the
    edges to those neighbors forms a Hamiltonian cycle in G.

For trivial instances with n <= 2 the source problem is always a NO
instance. We therefore output a target instance that is also a NO
instance (n = 0, empty edge list).

The reduction runs in O(n + |E|) time, i.e., polynomial.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian Cycle instance to a Hamiltonian Path instance.

    Parameters
    ----------
    instance: dict
        The source instance with keys "n" and "edges".

    Returns
    -------
    dict
        A target instance suitable for the Hamiltonian Path problem.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge cases: for n <= 2 the source is always NO. Return a trivial NO
    # instance for the target (n = 0).
    if n <= 2:
        return {"n": 0, "edges": []}

    # Choose vertex 0 as the distinguished vertex.
    # Determine its neighbors.
    neighbors: List[int] = []
    for u, v in edges:
        if u == 0:
            neighbors.append(v)
        elif v == 0:
            neighbors.append(u)

    # Build the edge list for the reduced graph.
    new_edges: List[List[int]] = []
    # Map original vertices 1..n-1 to new indices 0..n-2.
    def map_vertex(x: int) -> int:
        # x is guaranteed >= 1
        return x - 1

    for u, v in edges:
        if u == 0 or v == 0:
            continue  # skip edges incident to the removed vertex
        new_u = map_vertex(u)
        new_v = map_vertex(v)
        new_edges.append([new_u, new_v])

    # Add the two new vertices s and t.
    s = n - 1          # index for the new start vertex
    t = n              # index for the new end vertex
    # Connect s and t to each neighbor of the removed vertex.
    for nb in neighbors:
        nb_mapped = map_vertex(nb)
        new_edges.append([s, nb_mapped])
        new_edges.append([t, nb_mapped])

    new_n = n + 1  # (n-1) original vertices + 2 new vertices
    return {"n": new_n, "edges": new_edges}

