"""Gold reduction: 1-in-3-SAT -> Exact Cover.            [test, less common]

SOURCE  1-in-3-SAT   {"num_vars": m, "clauses": [[a, b, c], ...]}  positive variables only;
                     yes iff some assignment makes EXACTLY ONE variable per clause true
TARGET  Exact Cover  {"universe_size", "sets"}  yes iff sets cover each element exactly once

Construction: elements X_v = v - 1 for each variable, then C_j = m + j for
each clause. For each variable v, two sets:
  * TRUE_v  = {X_v} + {C_j for every clause j that contains v}
  * FALSE_v = {X_v}
"""


def reduce(instance):
    m, clauses = instance["num_vars"], instance["clauses"]
    sets = []
    for v in range(1, m + 1):
        true_set = [v - 1] + [m + j for j, clause in enumerate(clauses) if v in clause]
        sets += [true_set, [v - 1]]
    return {"universe_size": m + len(clauses), "sets": sets}