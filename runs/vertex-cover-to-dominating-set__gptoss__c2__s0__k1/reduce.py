"""Reduction from Vertex Cover to Dominating Set.

Given a Vertex Cover instance (graph G with n vertices, edge list, and integer k),
construct a Dominating Set instance G' and k' such that G has a vertex cover of
size at most k iff G' has a dominating set of size at most k'.

Construction:
  * Let m = number of edges in G.
  * For each edge e = (u, v) create a new vertex w_e (indexed n + i for the i‑th
    edge) and connect it to u and v.  These are the only edges incident to w_e.
    (We keep the original edges as well – they do not affect correctness.)
  * Let I be the set of isolated vertices in G (vertices of degree 0).
    Those vertices must be dominated directly in the dominating‑set instance.
  * The new graph has N' = n + m vertices.
  * Set k' = k + |I| + m.

Correctness sketch:
  * If C is a vertex cover of G with |C| ≤ k, then D = C ∪ I ∪ {w_e : e ∈ E}
    dominates G' and |D| = |C| + |I| + m ≤ k'.
  * Conversely, any dominating set D' of size ≤ k' can be transformed (by
    replacing each w_e in D' with one of its endpoints) into a dominating set
    D'' containing only original vertices.  D'' must contain at least one
    endpoint of every edge e to dominate w_e, thus the set C = D'' \ I is a
    vertex cover of G with |C| ≤ k.
  * The transformation runs in polynomial time.
"""

import copy

def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge case: source k < 0 => always NO. Return a trivially NO dominating set instance.
    if k < 0:
        return {"n": 0, "edges": [], "k": -1}

    # Compute degree to find isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated_count = sum(1 for d in degree if d == 0)

    m = len(edges)
    new_edges = copy.deepcopy(edges)  # keep original edges (optional)

    # Add a new vertex for each edge, connected to its endpoints.
    for idx, (u, v) in enumerate(edges):
        new_vertex = n + idx
        new_edges.append([new_vertex, u])
        new_edges.append([new_vertex, v])

    new_instance = {
        "n": n + m,          # original vertices + one new per edge
        "edges": new_edges,
        "k": k + isolated_count + m,
    }
    return new_instance

if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    json.dump(reduce(data), sys.stdout)
