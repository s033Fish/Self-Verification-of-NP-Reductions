"""Gold reduction: 3-SAT -> Exact Cover.             [difficulty: 7 of 8]

SOURCE  3-SAT        {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
        3 literals per clause on 3 different variables; yes iff satisfiable.
TARGET  Exact Cover  {"universe_size": u, "sets": [[element, ...], ...]}
        yes iff some of the sets cover every element 0..u-1 EXACTLY ONCE.

Construction (one element per variable, per clause and per literal occurrence)
  Let c = number of clauses. Number the universe in three blocks:
    * variable elements   X_v       for v = 1..m           (m elements)
    * clause elements     C_j       for j = 0..c-1          (c elements)
    * occurrence elements P_{j,k}   for literal k = 0,1,2 of clause j  (3c)
  so universe_size = m + 4c.

  Sets:
  1. For each variable v, two sets; choosing one means picking v's value:
       TRUE_v  = {X_v} + every occurrence of the literal  -v
       FALSE_v = {X_v} + every occurrence of the literal  +v
     X_v must be covered exactly once, so exactly one of them is chosen, and
     it covers exactly the occurrences that are FALSE under that assignment.
  2. For each clause j and each k: the set {C_j, P_{j,k}}.
     C_j must be covered exactly once, by an occurrence that is still
     uncovered, i.e. a TRUE literal. So every clause needs a true literal.
  3. For each clause j and each k: the singleton {P_{j,k}}, to cover the
     remaining true occurrences that step 2 did not use.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    c = len(clauses)

    def variable(v):
        return v - 1

    def clause(j):
        return m + j

    def occurrence(j, k):
        return m + c + 3 * j + k

    def occurrences_of(literal):
        return [occurrence(j, k)
                for j, current in enumerate(clauses)
                for k, l in enumerate(current) if l == literal]

    sets = []
    for v in range(1, m + 1):
        sets.append([variable(v)] + occurrences_of(-v))
        sets.append([variable(v)] + occurrences_of(v))
    for j in range(c):
        for k in range(3):
            sets.append([clause(j), occurrence(j, k)])
            sets.append([occurrence(j, k)])
    return {"universe_size": m + 4 * c, "sets": sets}