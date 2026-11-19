"""Polynomial-time reduction from Exact Cover to SAT.

Source (Exact Cover): {"universe_size": u, "sets": [[element, ...], ...]}
Target (SAT):         {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable x_i for every set i (1-indexed), meaning
"set i is selected".  For each universe element e:

  * add the clause  { x_i : e in set_i }   -- e must be covered by some
    selected set.  If no set contains e this clause is empty, correctly
    making the formula unsatisfiable.
  * for every pair i < j of sets that both contain e, add the clause
    { -x_i, -x_j }  -- e must not be covered twice.

A satisfying assignment selects a sub-collection of sets that covers every
element at least once (first family of clauses) and at most once (second
family), i.e. an exact cover.  Conversely an exact cover satisfies all
clauses.  Empty sets get a variable that is unconstrained, which is
harmless.  Duplicate non-empty sets are handled by the pairwise clauses.

The number of clauses is O(u * s^2) where s = number of sets, so the
reduction runs in polynomial time in the instance size.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    num_vars = len(sets)
    clauses = []

    # Precompute, for each element, the list of set indices containing it.
    covering = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        var = index + 1
        for element in subset:
            covering[element].append(var)

    for element in range(universe_size):
        vars_here = covering[element]
        # At least one selected set must cover this element.
        clauses.append(list(vars_here))
        # At most one selected set may cover this element.
        for a in range(len(vars_here)):
            va = vars_here[a]
            for b in range(a + 1, len(vars_here)):
                clauses.append([-va, -vars_here[b]])

    return {"num_vars": num_vars, "clauses": clauses}
