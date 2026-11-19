"""Polynomial-time reduction from 1-in-3-SAT (positive) to Exact Cover.

Idea
----
An exact cover instance is a universe plus a family of sets; a solution picks
pairwise-disjoint sets whose union is the whole universe, i.e. every universe
element is covered *exactly once*.

For 1-in-3-SAT we take the universe to be the clauses (element j = clause j),
and for every variable i we add the set of clause indices that contain i.
Choosing a collection of variables therefore covers clause j exactly once iff
exactly one chosen variable occurs in clause j -- which is exactly the
1-in-3-SAT condition.  Variables that occur in no clause yield empty sets,
which never affect an exact cover (matching the "variables need not appear"
edge case).  A formula with no clauses gives universe_size = 0, which is a
"yes" instance, matching the source edge case.

The construction is clearly polynomial: one set per variable, one element per
clause.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a positive 1-in-3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Universe element j corresponds to clause j.
    sets: list[list[int]] = []
    for var in range(1, num_vars + 1):
        containing = [j for j, clause in enumerate(clauses) if var in clause]
        sets.append(containing)

    return {"universe_size": len(clauses), "sets": sets}
