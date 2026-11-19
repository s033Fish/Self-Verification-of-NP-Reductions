"""Polynomial-time reduction from 3-SAT (ThreeSat) to NAE-3-SAT (NaeThreeSat).

Gadget: introduce one global fresh variable z, and for each source clause
(l1 or l2 or l3) introduce a fresh variable y_i and the two NAE clauses

    NAE(l1, l2, y_i)
    NAE(~y_i, l3, z)

Claim: the resulting NAE-3-SAT instance is satisfiable iff the source 3-SAT
instance is.

(=>) Suppose the source formula has a satisfying assignment A.  Set z=false.
For each clause:
  * if l1 = l2 = false then (since A satisfies the clause) l3 = true; set
    y_i = true.  Clause 1 is (false,false,true): not all equal.  Clause 2 is
    (~true, true, false) = (false,true,false): not all equal.
  * otherwise set y_i = false.  If l1 != l2, clause 1 is not all equal.
    If l1 = l2 = true, clause 1 is (true,true,false): not all equal.
    Clause 2 is (true, l3, false): not all equal since the first and third
    literals differ.
So the NAE instance is satisfiable.

(<=) Suppose the NAE instance has a satisfying assignment B.  NAE clauses are
invariant under complementing every variable, so if B(z)=true replace B by its
complement; the result still satisfies every clause and now has z=false.
For each gadget, NAE(l1,l2,y_i) and NAE(~y_i,l3,false) hold.  If l1=l2=false
then clause 1 forces y_i=true, and then clause 2 is (~true, l3, false) =
(false, l3, false), which is not all equal only if l3=true.  Hence every
source clause has a true literal under the restriction of B to the original
variables, so the source formula is satisfiable.

The reduction adds one variable per clause plus one global variable, so it is
linear time and linear size.
"""

from __future__ import annotations

from problems import NaeThreeSat, ThreeSat


def reduce(instance: dict) -> dict:
    """Reduce a 3-SAT instance to a NAE-3-SAT instance.

    Both instances use the format {"num_vars": m, "clauses": [[l1, l2, l3], ...]}.
    """
    ThreeSat.validate(instance)

    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    k = len(clauses)

    # Global variable shared by every gadget; original variables are 1..num_vars.
    z = num_vars + 1

    new_clauses: list[list[int]] = []
    for i, clause in enumerate(clauses):
        l1, l2, l3 = clause
        y = num_vars + 1 + (i + 1)  # fresh variable, distinct for each clause
        new_clauses.append([l1, l2, y])
        new_clauses.append([-y, l3, z])

    result = {"num_vars": num_vars + k + 1, "clauses": new_clauses}
    NaeThreeSat.validate(result)
    return result
