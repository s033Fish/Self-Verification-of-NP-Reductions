"""Polynomial-time reduction from Exact Cover to SAT.

Source instance (Exact Cover):
    {"universe_size": u, "sets": [[element, ...], ...]}
Target instance (SAT / CNF):
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Reduction
---------
Create one boolean variable x_i (numbered i + 1) for every set i, meaning
"set i is chosen".

* For every universe element e, add the clause

      [x_i for every set i that contains e]

  which forces at least one chosen set to cover e.  If no set contains e,
  this clause is empty and the formula is unsatisfiable, exactly as the
  Exact Cover instance is.

* For every pair of sets i < j that share at least one element, add the
  clause

      [-x_i, -x_j]

  which forbids choosing both.  This enforces pairwise disjointness of the
  chosen sets (in particular it forbids choosing two copies of the same
  non-empty set).

Empty sets become variables that occur in no clause; they are harmless
because choosing an empty set covers nothing and conflicts with nothing.
For u = 0 there are no coverage clauses, so the empty formula is
satisfiable (choose no sets), matching the yes-instance u = 0.

The formula is satisfiable iff the chosen sets form an exact cover: the
coverage clauses guarantee every element is covered, and the disjointness
clauses guarantee no element is covered twice.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # cover[e] = list of variables (1-based) of sets containing element e.
    cover = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        variable = index + 1
        for element in subset:
            cover[element].append(variable)

    clauses = []

    # At least one chosen set must cover each element.
    for element in range(universe_size):
        clauses.append(list(cover[element]))

    # Chosen sets must be pairwise disjoint.
    for i in range(num_sets):
        set_i = sets[i]
        if not set_i:
            continue
        members_i = set(set_i)
        for j in range(i + 1, num_sets):
            set_j = sets[j]
            if not set_j:
                continue
            if any(element in members_i for element in set_j):
                clauses.append([-(i + 1), -(j + 1)])

    return {"num_vars": num_sets, "clauses": clauses}
