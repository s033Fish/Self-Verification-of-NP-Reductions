"""Polynomial-time reduction from Exact Cover to SAT.

Exact Cover instance: {"universe_size": u, "sets": [[element, ...], ...]}
SAT instance:         {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Introduce one boolean variable per set: variable i+1 is true iff set i is
chosen.

1. For every element e of the universe, add the clause consisting of the
   positive literals of all sets that contain e.  This forces e to be
   covered by at least one chosen set.  If no set contains e, the clause is
   empty and the formula is unsatisfiable, as it should be.

2. For every pair of sets that share an element, add the clause
   (-x_i or -x_j).  This forbids choosing both, i.e. it forces the chosen
   sets to be pairwise disjoint (each element covered at most once).

A satisfying assignment therefore selects a pairwise-disjoint collection of
sets whose union is the whole universe: an exact cover.  Conversely, any
exact cover yields a satisfying assignment.  The construction is polynomial:
at most sum_e k_e^2 clauses in step 2, where k_e is the number of sets
containing e, and at most u + total-element-occurrences clauses overall.
"""


def reduce(instance):
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # element -> list of set indices containing it
    containing = [[] for _ in range(universe_size)]
    for index, subset in enumerate(sets):
        for element in subset:
            containing[element].append(index)

    clauses = []

    # At least one chosen set per element.
    for element in range(universe_size):
        clauses.append([index + 1 for index in containing[element]])

    # At most one chosen set per element: any two sets sharing an element
    # cannot both be selected.
    for indices in containing:
        for a in range(len(indices)):
            ia = indices[a]
            for b in range(a + 1, len(indices)):
                ib = indices[b]
                clauses.append([-(ia + 1), -(ib + 1)])

    return {"num_vars": num_sets, "clauses": clauses}
