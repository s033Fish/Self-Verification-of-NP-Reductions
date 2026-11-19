"""Polynomial-time reduction from 3-SAT to Exact Cover.

Construction
------------
Given a 3-CNF formula with m variables and k clauses, build a universe:

  * p_i        for each variable i (1..m)
  * occ(j, t)  for each literal occurrence (clause j, position t)
  * c_j        for each clause j

Sets:

  * T_i = {p_i} u {occ(j,t) : clause j contains the negative literal -i}
  * F_i = {p_i} u {occ(j,t) : clause j contains the positive literal +i}
  * {c_j, occ(j,t)}  for every literal occurrence
  * {occ(j,t)}       singleton for every literal occurrence

Choosing T_i represents x_i = true, choosing F_i represents x_i = false.
Both contain p_i, so an exact cover chooses exactly one of them.

A positive occurrence element of variable i lives in F_i, hence it is left
uncovered exactly when x_i is true.  A negative occurrence element lives in
T_i, hence it is left uncovered exactly when x_i is false.  The clause
element c_j can only be covered by one of the sets {c_j, occ(j,t)}, and such
a set is disjoint from the chosen variable set exactly when the associated
literal is true.  Therefore c_j is coverable iff clause j has a true literal.

Singleton sets let occurrence elements of true literals that are not used to
cover their clause be covered without touching c_j, so clauses with several
true literals cause no problem.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    k = len(clauses)

    universe_size = num_vars + 4 * k

    def pivot(i):
        return i - 1

    def occurrence(j, t):
        return num_vars + 3 * j + t

    def clause_element(j):
        return num_vars + 3 * k + j

    # T_i (x_i true) and F_i (x_i false); both contain the pivot p_i.
    true_sets = [[] for _ in range(num_vars + 1)]
    false_sets = [[] for _ in range(num_vars + 1)]
    for i in range(1, num_vars + 1):
        true_sets[i].append(pivot(i))
        false_sets[i].append(pivot(i))

    sets = []
    for j, clause in enumerate(clauses):
        c = clause_element(j)
        for t, literal in enumerate(clause):
            o = occurrence(j, t)
            v = abs(literal)
            if literal > 0:
                # Positive occurrence: free exactly when x_v is true.
                false_sets[v].append(o)
            else:
                # Negative occurrence: free exactly when x_v is false.
                true_sets[v].append(o)
            sets.append([c, o])  # clause set
            sets.append([o])     # singleton for the occurrence

    for i in range(1, num_vars + 1):
        sets.append(true_sets[i])
        sets.append(false_sets[i])

    return {"universe_size": universe_size, "sets": sets}
