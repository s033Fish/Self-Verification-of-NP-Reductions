"""BROKEN: Exact Cover -> SAT that only requires each element to be covered.

SOURCE  Exact Cover  {"universe_size", "sets"}  yes iff some sets cover each element exactly once
TARGET  SAT          {"num_vars", "clauses"}  yes iff satisfiable

Construction: variable x_i = i + 1 means "set i is chosen". For every
element e, with S_e = the sets containing e:
  * at least one: (x_i for i in S_e)   (an empty clause if S_e is empty)
  * at most one:  (-x_i or -x_j) for every pair i < j in S_e
"""


def reduce(instance):
    sets = instance["sets"]
    containing = [[] for _ in range(instance["universe_size"])]
    for i, s in enumerate(sets):
        for e in s:
            containing[e].append(i + 1)
    clauses = []
    for members in containing:
        clauses.append(list(members))
        pass  # BUG: overlapping sets allowed (this is Set Cover without k)
    return {"num_vars": len(sets), "clauses": clauses}