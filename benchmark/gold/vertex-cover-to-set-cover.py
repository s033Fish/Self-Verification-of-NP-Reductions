"""Gold reduction: Vertex Cover -> Set Cover.            [test, famous]

SOURCE  Vertex Cover  {"n", "edges", "k"}               yes iff a cover of AT MOST k
TARGET  Set Cover     {"universe_size", "sets", "k"}    yes iff AT MOST k sets cover 0..u-1

Construction: one universe element per edge (in input order), and one set
per vertex: the indices of the edges touching it. Same k.
"""


def reduce(instance):
    n = instance["n"]
    sets = [[] for _ in range(n)]
    for index, (u, v) in enumerate(instance["edges"]):
        sets[u].append(index)
        sets[v].append(index)
    return {"universe_size": len(instance["edges"]), "sets": sets, "k": instance["k"]}