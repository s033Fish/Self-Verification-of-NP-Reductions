"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Construction (standard edge-subdivision gadget):
    Given G = (V, E), let V' be the set of non-isolated vertices of G.
    Isolated vertices never help a vertex cover, and in the target graph
    they would be forced into every dominating set, so we drop them.

    Build H with
        V(H) = V'  union  { x_e : e in E }
        E(H) = (E restricted to V')  union  { {u, x_e}, {v, x_e} : e = {u,v} }.

    Return H with the same k.

Claim: G has a vertex cover of size <= k  iff  H has a dominating set of
size <= k.

(=>) If C is a vertex cover of G (equivalently of G[V']), then C dominates
H: every x_e is adjacent to an endpoint in C, and every non-isolated
vertex v not in C has an incident edge whose other endpoint lies in C.

(<=) If D dominates H, then C = (D cap V') plus, for every x_e in D whose
two endpoints are outside D, one arbitrary endpoint of e, is a vertex
cover of G[V'] with |C| <= |D|.  Indeed x_e is adjacent only to its two
endpoints, so for each edge e at least one endpoint of e is in D or x_e
is in D (and then C contains an endpoint of e).

Vertices are relabelled to 0..n'-1.
"""
from __future__ import annotations


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    used = set()
    for u, v in edges:
        used.add(u)
        used.add(v)
    verts = sorted(used)
    index = {v: i for i, v in enumerate(verts)}
    n0 = len(verts)
    m = len(edges)

    new_edges = []
    # original edges among the non-isolated vertices, relabelled
    for u, v in edges:
        new_edges.append([index[u], index[v]])
    # one subdivision vertex per edge, joined to both endpoints
    for j, (u, v) in enumerate(edges):
        x = n0 + j
        new_edges.append([index[u], x])
        new_edges.append([index[v], x])

    return {"n": n0 + m, "edges": new_edges, "k": k}
