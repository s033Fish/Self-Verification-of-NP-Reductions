"""Polynomial-time reduction from Exact Cover to SAT.

Source instance format:
    {"universe_size": u, "sets": [[element, ...], ...]}

Target instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}

Construction
------------
Create one Boolean variable x_i for each input set i (1-indexed in SAT).

Let occurrences[e] be the list of SAT variables for sets containing element e.

* For every element e that occurs in at least one input set, add the clause
      (x_i1 OR x_i2 OR ... OR x_ik)
  where i1..ik are exactly the sets containing e.  This forces every element
  to be covered by at least one chosen set.

* If the number of distinct occurring elements is less than u, then some
  universe element occurs in no set.  Add the empty clause [] to make the
  formula unsatisfiable, as no exact cover can exist.

* For every element e, and every pair i < j of sets containing e, add
      (not x_i OR not x_j).
  This forces chosen sets to be pairwise disjoint.  Two copies of the same
  non-empty set share all their elements, so they cannot both be chosen.

A satisfying assignment chooses exactly a pairwise-disjoint collection of
sets covering every element, i.e. an exact cover.  Conversely, any exact
cover gives a satisfying assignment by setting its sets true and all other
sets false.

Empty input sets produce variables that occur in no coverage or disjointness
clause, so they may be assigned either value and never affect satisfiability.
For u = 0 there are no occurring elements, so there are no clauses at all and
the empty CNF is satisfiable, as required.

The construction uses time polynomial in the input size: O(total element
occurrences + sum over elements of (number of sets containing it)^2), which
is bounded by a polynomial in the number of sets and total set sizes.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT (CNF) instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]

    num_sets = len(sets)
    num_vars = num_sets

    # occurrences[element] = list of 1-indexed SAT variables for sets
    # containing that element.
    occurrences: dict[int, list[int]] = {}
    for index, current_set in enumerate(sets):
        variable = index + 1
        for element in current_set:
            occurrences.setdefault(element, []).append(variable)

    clauses: list[list[int]] = []

    # If some universe element is absent from every set, no exact cover
    # exists.  The universe has exactly universe_size elements (0..u-1), and
    # valid instances contain no elements outside that range, so comparing
    # the number of distinct occurring elements with u detects this.
    if len(occurrences) < universe_size:
        clauses.append([])

    # Every occurring element must be covered by at least one chosen set.
    for variables in occurrences.values():
        clauses.append(list(variables))

    # Chosen sets must be pairwise disjoint.  For each element, no two sets
    # containing it may both be chosen.
    for variables in occurrences.values():
        count = len(variables)
        for i in range(count):
            variable_i = variables[i]
            for j in range(i + 1, count):
                clauses.append([-variable_i, -variables[j]])

    return {"num_vars": num_vars, "clauses": clauses}
