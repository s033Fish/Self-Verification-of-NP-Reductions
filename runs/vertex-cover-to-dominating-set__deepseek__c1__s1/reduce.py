"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Given a Vertex Cover instance G = (V, E) with parameter k, build the
classic dominating-set gadget: keep every original vertex and every
original edge, and for every edge {u, v} add a fresh vertex w_{uv}
adjacent to both u and v.

Let I be the set of isolated vertices of G.  Then

    G has a vertex cover of size <= k
        iff
    the gadget graph H has a dominating set of size <= k + |I|.

Proof sketch
------------
(=>) If C is a vertex cover of G with |C| <= k, then C u I dominates H:
     isolated vertices dominate themselves; every non-isolated vertex is
     either in C or adjacent to a vertex of C (its incident edge is
     covered by C); and each gadget vertex w_{uv} is adjacent to an
     endpoint of {u, v} that lies in C.  Hence DS(H) <= k + |I|.

(<=) Let D be a dominating set of H with |D| <= k + |I|.  A gadget
     vertex w_{uv} in D can be swapped for one of its endpoints u or v
     without losing domination (w's only neighbours are u and v), so we
     may assume D contains no gadget vertex.  Then D n V(G) is a vertex
     cover of G: for every edge {u, v}, the gadget vertex w_{uv} must be
     dominated, so u or v lies in D.  Moreover every isolated vertex of
     G has no neighbour in H and therefore lies in D.  Removing the
     |I| isolated vertices leaves a vertex cover of size
     <= (k + |I|) - |I| = k.  Hence VC(G) <= k.

The construction uses O(n + |E|) time and space, so it is polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always a "no" instance of Vertex Cover.  Map it to an
    # obviously "no" Dominating Set instance (k < 0 is always no there).
    if k < 0:
        return {"n": 0, "edges": [], "k": -1}

    # Count isolated vertices of the source graph.
    touched = [False] * n
    for u, v in edges:
        touched[u] = True
        touched[v] = True
    isolated = sum(1 for v in range(n) if not touched[v])

    # Target graph: original vertices keep their labels; each source edge
    # gets a fresh gadget vertex n + i adjacent to both of its endpoints.
    new_edges = [[u, v] for u, v in edges]
    for i, (u, v) in enumerate(edges):
        w = n + i
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": n + len(edges), "edges": new_edges, "k": k + isolated}
