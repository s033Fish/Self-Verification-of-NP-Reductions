"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Construction
------------
Introduce one global fresh variable y and, for every source clause
(l1 v l2 v l3), one fresh variable z.  Replace that clause by the two
NAE clauses

    NAE(l1, l2, z)        and        NAE(~z, l3, y).

Claim: with y = false, the pair is satisfiable over the choice of z iff
(l1 v l2 v l3) holds.
  * NAE(~z, l3, false) forces ~z v l3, i.e. z -> l3.
  * NAE(l1, l2, z) then requires l1 v l2 v l3.
  Conversely a suitable z exists whenever the original clause holds.

Forward direction: a satisfying assignment of the 3-SAT instance
extends to the NAE instance by putting y = false and choosing each z.

Reverse direction: NAE clauses are invariant under complementing all
variables, so any satisfying assignment of the NAE instance can be
complemented to one with y = false; there the claim forces every
original clause to be true.

The construction is linear in the number of clauses, hence polynomial.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    y = m + 1
    new_clauses = []
    for i, clause in enumerate(clauses):
        z = m + 2 + i
        l1, l2, l3 = clause
        new_clauses.append([l1, l2, z])
        new_clauses.append([-z, l3, y])

    return {"num_vars": m + 1 + len(clauses), "clauses": new_clauses}
