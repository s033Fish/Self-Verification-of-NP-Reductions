"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Construction
------------
Given a Vertex Cover instance G = (V, E) with |V| = n and |E| = m, build a
Dominating Set instance G' as follows.

* Keep every original vertex of G.
* For every edge e_i = (u, v) of G (i = 0 .. m-1) add a fresh vertex w_i and
  connect it to both u and v.

So G' has n' = n + m vertices and edges
    E' = E  union  { {u, w_i}, {v, w_i} : e_i = (u, v) }.

Correctness
-----------
Let I be the set of isolated vertices of G (degree 0).  An isolated vertex of
G stays isolated in G', hence every dominating set of G' must contain I.
On the remaining part of G' one has the usual equivalence:

    D is a dominating set of G' \ I  <=>  D is a vertex cover of G

(=>) every gadget vertex w_i has neighbours exactly u and v, so D must contain
u or v for each edge; (<=) a vertex cover hits an endpoint of every edge, so it
dominates every original vertex and every gadget vertex.

Therefore  min-dominating-set(G') = |I| + min-vertex-cover(G), and the answer
to the produced instance is yes iff the answer to the input is yes when we set

    k' = k + |I|.

Edge cases
----------
* k < 0: k' = k + |I| < |I| <= min-dominating-set(G'), so the output is no,
  matching the source (always no).
* No edges: I = V, min-vertex-cover(G) = 0, min-dominating-set(G') = n, and
  k' = k + n; the output is yes exactly when k >= 0, matching the source.
* k >= n: source is yes; min-dominating-set(G') = |I| + minVC(G) <= |I| + n
  <= |I| + k = k', so the output is yes as well.
* n = 0: then m = 0, I = 0, k' = k, and both problems are yes iff k >= 0.
"""


def reduce(instance):
    """Return a Dominating Set instance equivalent to the Vertex Cover input."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    m = len(edges)

    # Count isolated vertices of the source graph.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    # Original edges plus, for each edge, a new vertex adjacent to its endpoints.
    new_edges = [list(e) for e in edges]
    for i, (u, v) in enumerate(edges):
        w = n + i
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": n + m, "edges": new_edges, "k": k + isolated}
