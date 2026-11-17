"""Polynomial-time reduction from 3-SAT (SOURCE) to Exact Cover (TARGET).

Given a 3-CNF formula with variables 1..m and clauses C_0..C_{K-1}, build an
exact-cover instance as follows.

Elements
--------
* a_i          for each variable i (0-indexed i = 0..m-1)
* c_j          for each clause j
* occ_{j,k}    for each clause j and literal position k in {0,1,2}

So universe_size = m + K + 3K = m + 4K.

Sets
----
Variable gadget for variable v (1-indexed):
    T_v = {a_v} U { occ_{j,k} : literal at (j,k) is -v }   # "v is true"
    F_v = {a_v} U { occ_{j,k} : literal at (j,k) is +v }   # "v is false"
Choosing exactly one of T_v, F_v covers a_v and every occurrence of a *false*
literal of v; occurrences of *true* literals stay free.

Clause gadget for clause j:
    {c_j, occ_{j,k}} for k = 0,1,2
To cover c_j exactly one of these is chosen, and it needs occ_{j,k} to be free,
i.e. literal (j,k) must be true.

Absorber:
    {occ_{j,k}} for every occurrence
Extra occurrences of true literals (those not used to cover their clause) are
covered by these singletons.  Occurrences of false literals are already covered
by the variable gadget, so a singleton can never be used for them.

Correctness
-----------
(=>) From a satisfying assignment choose T_v/F_v per variable and, for each
clause, the clause set of one true literal; cover all remaining true
occurrences with singletons.  Every element is covered exactly once.

(<=) In any exact cover, a_v forces exactly one of T_v/F_v, defining an
assignment.  c_j is covered by some {c_j, occ_{j,k}} whose occurrence is free,
so literal (j,k) is true and clause j is satisfied.

The construction uses O(m + K) elements and sets, so it runs in polynomial time
and never calls a brute-force solver.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a 3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # Element layout:
    #   a_i        -> i                        (i in 0..num_vars-1)
    #   c_j        -> num_vars + j             (j in 0..num_clauses-1)
    #   occ_{j,k}  -> num_vars + num_clauses + 3*j + k
    universe_size = num_vars + 4 * num_clauses

    def occ(j: int, k: int) -> int:
        return num_vars + num_clauses + 3 * j + k

    sets: list[list[int]] = []

    # Variable gadgets: T_v covers occurrences of -v, F_v covers +v.
    for v in range(1, num_vars + 1):
        a = v - 1
        true_set = [a]
        false_set = [a]
        for j, clause in enumerate(clauses):
            for k, literal in enumerate(clause):
                if literal == -v:
                    true_set.append(occ(j, k))
                elif literal == v:
                    false_set.append(occ(j, k))
        sets.append(true_set)
        sets.append(false_set)

    # Clause gadgets and absorbers.
    for j in range(num_clauses):
        c = num_vars + j
        for k in range(3):
            o = occ(j, k)
            sets.append([c, o])  # cover clause j via a true literal occurrence
            sets.append([o])     # absorb an unused true occurrence

    return {"universe_size": universe_size, "sets": sets}
