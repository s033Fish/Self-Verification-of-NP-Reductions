"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"n": n', "edges": [[u, v], ...], "k": k'}

Construction
------------
Given a source graph G = (V, E), build a target graph G' as follows:

  * Keep every original vertex in V.
  * For every edge e = (u, v) in E, add one new vertex x_e and connect it
    to both u and v.  (No other new edges are added.)

Let iso be the number of isolated vertices of G (vertices of degree 0).
The target budget is k' = k + iso, and the target graph has
n' = n + |E| vertices.

Correctness
-----------
(=>) Let C be a vertex cover of G with |C| <= k.  Then
     D = C union {isolated vertices of G} is a dominating set of G':
       * every original vertex v is either in D, or is non-isolated and
         has an incident edge e = (v, w) whose endpoint w lies in C
         (since C covers e), so v is adjacent to w in D;
       * every edge-vertex x_e is adjacent to u and v, and C covers e,
         so at least one of u, v lies in C (hence in D).
     Also |D| <= k + iso = k'.

(<=) Let D be a dominating set of G' with |D| <= k'.  Every isolated
     original vertex has no neighbours, so it must belong to D.  For any
     edge e = (u, v) of G, the edge-vertex x_e has neighbours exactly
     u and v, so D must contain u or v.  Hence D restricted to the
     non-isolated original vertices is a vertex cover of G, and
     |D restricted| <= |D| - iso <= k' - iso = k.

Therefore G has a vertex cover of size at most k iff G' has a dominating
set of size at most k'.  The construction runs in O(n + |E|) time.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Degrees in the source graph, to find isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    # Original edges plus, for each edge e = (u, v), a new vertex x_e
    # adjacent to both endpoints.
    new_edges = [[u, v] for u, v in edges]
    for index, (u, v) in enumerate(edges):
        x = n + index
        new_edges.append([u, x])
        new_edges.append([v, x])

    return {
        "n": n + len(edges),
        "edges": new_edges,
        "k": k + isolated,
    }
