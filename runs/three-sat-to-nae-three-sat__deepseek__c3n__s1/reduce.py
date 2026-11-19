"""Polynomial-time reduction from 3-SAT (SOURCE) to NAE-3-SAT (TARGET).

Idea
----
Introduce one global fresh variable ``f``.  For every source clause
``(l1 v l2 v l3)`` introduce a fresh variable ``z_i`` and emit the two
NAE-3 clauses::

    NAE(l1, l2, z_i)
    NAE(~z_i, l3, f)

Claim: the conjunction of those two NAE-3 clauses is equivalent to the
NAE-4 clause ``NAE(l1, l2, l3, f)``.

  * (=>) If both NAE-3 clauses hold but l1=l2=l3=f=v, then the first clause
    forces z_i != v while the second forces ~z_i != v, i.e. z_i = v -- a
    contradiction.
  * (<=) If NAE(l1,l2,l3,f) holds, a suitable z_i exists:
      - if l1 != l2, pick z_i = l1 (first clause is fine, and the second
        clause can always be satisfied by a suitable choice; more carefully,
        if l3 = f pick z_i = l3 so ~z_i != l3 = f, else the second clause is
        automatically not-all-equal);
      - if l1 = l2, pick z_i = ~l1; the first clause becomes (l1,l1,~l1)
        which is not all equal, and since not all four are equal at least one
        of l3, f differs from l1 = l2, so (l1, l3, f) is not all equal.

Now, if f = false then NAE(l1,l2,l3,false) says at least one of l1,l2,l3 is
true, i.e. the source clause is satisfied.  If f = true then it says at least
one of l1,l2,l3 is false, i.e. the *complement* of the assignment satisfies
the source clause.  Since complementing an assignment preserves
satisfiability, the source formula is satisfiable iff the target formula is.

The construction is linear in the size of the source instance, hence
polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to a NAE-3-SAT instance.

    Both instances use the format
    ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # A formula with no clauses is trivially satisfiable in both problems.
    if not clauses:
        return {"num_vars": num_vars, "clauses": []}

    k = len(clauses)
    f = num_vars + 1  # global fresh variable

    out_clauses: list[list[int]] = []
    for i, clause in enumerate(clauses):
        l1, l2, l3 = clause
        z = f + 1 + i  # fresh variable for this clause
        out_clauses.append([l1, l2, z])
        out_clauses.append([-z, l3, f])

    return {"num_vars": f + k, "clauses": out_clauses}
