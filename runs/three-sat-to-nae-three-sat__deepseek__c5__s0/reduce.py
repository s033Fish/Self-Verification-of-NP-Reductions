"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Idea
----
NAE clauses are invariant under flipping *all* variables (complementing every
variable turns a not-all-equal clause into a not-all-equal clause).  Therefore
we may use a single global variable ``z`` as a reference: any satisfying
assignment of the produced NAE formula can be flipped so that ``z`` is false,
and flipping preserves satisfaction.

For every source clause C = (l1 or l2 or l3) we introduce a fresh variable y
and emit the two NAE clauses

        NAE(l1, l2, y)      and      NAE(not y, l3, z)

Claim: with z = false this gadget is satisfiable (over y) exactly when
(l1 or l2 or l3) holds.

    * If (l1 or l2 or l3) holds, pick y = not(l1 or l2): then l1, l2, y are
      not all equal, and (not y, l3, false) is not all equal because not y is
      true while z is false.
    * If l1 = l2 = l3 = false, then NAE(l1, l2, y) forces y = true, and then
      NAE(not y, l3, z) = NAE(false, false, false), which is all-equal, so the
      gadget is unsatisfiable.

Consequently the whole construction is satisfiable iff the source is:
    * source satisfiable  => set z = false and satisfy every gadget;
    * target satisfiable  => if z is false, every gadget forces its clause to
      have a true literal; if z is true, every gadget forces its clause to have
      a false literal, so the complementary assignment satisfies the source.

The reduction adds one variable and two clauses per source clause, so it runs
in linear (hence polynomial) time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to an equisatisfiable NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    z = num_vars + 1  # global reference variable
    new_clauses: list[list[int]] = []
    for index, clause in enumerate(clauses):
        l1, l2, l3 = clause
        y = num_vars + 2 + index  # fresh variable per source clause
        new_clauses.append([l1, l2, y])
        new_clauses.append([-y, l3, z])

    return {"num_vars": num_vars + 1 + len(clauses), "clauses": new_clauses}
