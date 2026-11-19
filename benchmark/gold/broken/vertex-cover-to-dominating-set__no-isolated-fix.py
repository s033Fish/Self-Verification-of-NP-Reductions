"""BROKEN: Vertex Cover -> Dominating Set without the +I for isolated vertices.

SOURCE  Vertex Cover    {"n", "edges", "k"}  yes iff a cover of AT MOST k
TARGET  Dominating Set  {"n", "edges", "k"}  yes iff a dominating set of AT MOST k

Construction: keep the graph and, for every edge uv, add a new vertex w_uv
adjacent to both u and v (a triangle on each edge). Let I be the number of
isolated vertices of the source. Set k' = k + I.

Why the I: an isolated vertex has no neighbours, so it must be in every
dominating set, but it is never needed in a vertex cover.

  Cover -> dominating set: take a cover C plus the isolated vertices. Each
  w_uv is dominated because u or v is in C. Each non-isolated vertex v has
  an edge vu; C contains v or u, so v is dominated. Size <= k + I.

  Dominating set -> cover: D contains all I isolated vertices. Replace each
  w_uv in D by u (still dominating, no larger). Now w_uv is dominated only
  through u or v, so D minus the isolated vertices covers every edge, with
  at most k vertices.

"""


def reduce(instance):
    n = instance["n"]
    edges = [list(e) for e in instance["edges"]]
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)
    out = list(edges)
    for index, (u, v) in enumerate(edges):
        w = n + index
        out.append([u, w])
        out.append([v, w])
    return {"n": n + len(edges), "edges": out, "k": instance["k"]}