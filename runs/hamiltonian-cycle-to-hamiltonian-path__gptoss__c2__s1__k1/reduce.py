"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem (HamiltonianCycle) expects an instance of the form:
    {"n": n, "edges": [[u, v], ...]}
where vertices are 0..n-1 and edges are undirected.

The target problem (HamiltonianPath) uses the same format.

We implement a classic polynomial‑time reduction using a vertex‑splitting
construction.  For each original vertex *v* we create two vertices
``v_in`` and ``v_out`` connected by an edge.  For each original edge
``(u, v)`` we connect ``u_out`` to ``v_in`` and ``v_out`` to ``u_in``.
Finally we add a new start vertex ``s`` connected to every ``v_in`` and a
new terminal vertex ``t`` connected from every ``v_out``.  The resulting
graph has a Hamiltonian *path* from ``s`` to ``t`` iff the original graph
has a Hamiltonian *cycle*.

Edge cases (n <= 2) are handled explicitly: Hamiltonian Cycle is always
"no" for these sizes, so we return a trivially unsatisfiable Hamiltonian
Path instance (n = 0, no edges).
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian Cycle instance to a Hamiltonian Path instance.

    Parameters
    ----------
    instance: dict
        ``{"n": n, "edges": [[u, v], ...]}`` describing an undirected graph.

    Returns
    -------
    dict
        An instance of the Hamiltonian Path problem with the property that
        the answer is *yes* exactly when the answer for the input instance
        is *yes*.
    """
    n = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # For n <= 2 the source problem is always a NO instance.  Return a
    # guaranteed NO instance for the target problem.
    if n <= 2:
        return {"n": 0, "edges": []}

    # New vertices: for each original vertex i we create i (in) and n+i (out).
    # Add two extra vertices: s = 2*n, t = 2*n + 1.
    s = 2 * n
    t = 2 * n + 1
    new_n = 2 * n + 2
    new_edges: List[List[int]] = []

    # Connect each in/out pair.
    for i in range(n):
        new_edges.append([i, n + i])  # edge (v_in, v_out)

    # For each original undirected edge {u, v}, add edges (u_out, v_in)
    # and (v_out, u_in).
    for u, v in edges:
        # Ensure we add each undirected edge only once.
        new_edges.append([n + u, v])
        new_edges.append([n + v, u])

    # Connect start vertex s to every v_in.
    for i in range(n):
        new_edges.append([s, i])

    # Connect every v_out to terminal vertex t.
    for i in range(n):
        new_edges.append([n + i, t])

    # The problem format expects undirected edges without duplicates.
    # We will remove possible duplicate entries by normalising each edge
    # (smaller vertex first) and using a set.
    seen = set()
    cleaned_edges: List[List[int]] = []
    for u, v in new_edges:
        if u == v:
            # Self‑loops are irrelevant for Hamiltonian path; skip.
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) not in seen:
            seen.add((a, b))
            cleaned_edges.append([a, b])

    return {"n": new_n, "edges": cleaned_edges}

