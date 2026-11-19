"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Idea
----
NAE-3-SAT is invariant under complementing *all* variables: flipping every
literal in a clause keeps the three literals "not all equal".  Therefore a
variable ``z`` may be used as a "false constant": any satisfying assignment
can be complemented so that ``z`` is false, and this operation preserves
satisfaction of the whole formula.

With ``z`` playing the role of a false literal, the standard gadget for a
3-SAT clause ``(l1 or l2 or l3)`` using one fresh variable ``y`` is:

    NAE(l1, l2, y)
    NAE(not y, l3, z)

For fixed ``l1, l2, l3`` and ``z = false`` this pair is satisfiable over ``y``
if and only if at least one of ``l1, l2, l3`` is true (checked exhaustively).

Correctness
-----------
* If the 3-SAT instance is satisfiable, take a satisfying assignment, set
  ``z = false`` and pick ``y`` for each gadget.  Every NAE clause holds.
* If the produced NAE instance is satisfiable, complement the whole
  assignment so that ``z = false`` (NAE-3-SAT is complement-invariant).
  Each gadget is then satisfiable, which forces ``l1 or l2 or l3`` to be true
  for every original clause.  Hence the 3-SAT instance is satisfiable.

The construction uses ``m + 1 + (#clauses)`` variables and ``2 * #clauses``
clauses, so it runs in linear (hence polynomial) time.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a 3-SAT instance to a NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # No clauses: already a yes-instance; an empty NAE formula is also yes.
    if not clauses:
        return {"num_vars": num_vars, "clauses": []}

    # z acts as a false constant (up to global complementation).
    z = num_vars + 1
    next_var = num_vars + 2

    out_clauses = []
    for clause in clauses:
        l1, l2, l3 = clause
        y = next_var
        next_var += 1
        out_clauses.append([l1, l2, y])
        out_clauses.append([-y, l3, z])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
