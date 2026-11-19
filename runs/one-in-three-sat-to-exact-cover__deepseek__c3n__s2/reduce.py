"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Idea
----
A positive 1-in-3-SAT instance is *already* an exact-cover instance in
disguise:

  * Make one universe element per clause (element j <-> clause j).
  * Make one set per variable x: the set of clause indices whose clause
    contains x.

Choosing a collection of variables corresponds to choosing the matching
sets.  A clause element is covered exactly once iff exactly one of the
chosen variables occurs in that clause.  Therefore an exact cover of all
clause elements exists iff there is an assignment making exactly one
variable true in every clause.

Variables that never occur produce empty sets, which never matter, so we
simply omit them.  The construction is linear in the total number of
literal occurrences.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to an Exact Cover instance."""
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # occurrence map: variable -> list of clause indices containing it
    occurrences: dict[int, list[int]] = {}
    for index, clause in enumerate(clauses):
        for variable in clause:
            occurrences.setdefault(variable, []).append(index)

    # One set per variable that actually occurs (sorted for determinism).
    sets = [occurrences[variable] for variable in sorted(occurrences)]

    return {"universe_size": num_clauses, "sets": sets}
