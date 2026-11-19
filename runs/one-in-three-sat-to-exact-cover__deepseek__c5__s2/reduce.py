"""Polynomial-time reduction from 1-in-3-SAT (positive) to Exact Cover.

Idea
----
For a variable x that occurs k times, create 2k elements:
    x^T_1, ..., x^T_k      ("x is true" copies)
    x^F_1, ..., x^F_k      ("x is false" copies)

Variable gadget: two sets
    T(x) = {x^T_1, ..., x^T_k}
    F(x) = {x^F_1, ..., x^F_k}
In any exact cover exactly one of them is used (the other would overlap the
clause sets), so the variable gets a single global truth value.

For each clause j = (a, b, c), let i_a, i_b, i_c be the occurrence indices of
this occurrence of a, b, c.  Create element p_j and three sets, one for each
of the three assignments with exactly one true literal:

    {p_j, a^F_{i_a}, b^T_{i_b}, c^T_{i_c}}   (a true,  b false, c false)
    {p_j, a^T_{i_a}, b^F_{i_b}, c^T_{i_c}}   (a false, b true,  c false)
    {p_j, a^T_{i_a}, b^T_{i_b}, c^F_{i_c}}   (a false, b false, c true)

They share p_j, so exactly one is chosen.  A set is usable only if the
variable gadget left the corresponding copies free, i.e. only if the global
truth values match the pattern.  Hence a cover exists iff the formula has an
assignment with exactly one true variable per clause.

The construction is linear in the input size, hence polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Number of occurrences of each variable.
    counts = [0] * (num_vars + 1)
    for clause in clauses:
        for var in clause:
            counts[var] += 1

    # Element ids are just consecutive integers; universe_size is their count.
    next_id = 0

    def new_element() -> int:
        nonlocal next_id
        eid = next_id
        next_id += 1
        return eid

    # Create the 2 * count copies for every used variable.
    true_copy: dict[tuple[int, int], int] = {}
    false_copy: dict[tuple[int, int], int] = {}
    for var in range(1, num_vars + 1):
        for i in range(1, counts[var] + 1):
            true_copy[(var, i)] = new_element()
            false_copy[(var, i)] = new_element()

    # One element per clause and the occurrence index of each of its literals.
    clause_element: list[int] = []
    occurrence: list[list[int]] = []
    used = [0] * (num_vars + 1)
    for clause in clauses:
        idxs = []
        for var in clause:
            used[var] += 1
            idxs.append(used[var])
        occurrence.append(idxs)
        clause_element.append(new_element())

    sets: list[list[int]] = []

    # Variable gadgets.
    for var in range(1, num_vars + 1):
        if counts[var] > 0:
            sets.append([true_copy[(var, i)] for i in range(1, counts[var] + 1)])
            sets.append([false_copy[(var, i)] for i in range(1, counts[var] + 1)])

    # Clause gadgets.
    for j, clause in enumerate(clauses):
        a, b, c = clause
        ia, ib, ic = occurrence[j]
        p = clause_element[j]
        sets.append([p, false_copy[(a, ia)], true_copy[(b, ib)], true_copy[(c, ic)]])
        sets.append([p, true_copy[(a, ia)], false_copy[(b, ib)], true_copy[(c, ic)]])
        sets.append([p, true_copy[(a, ia)], true_copy[(b, ib)], false_copy[(c, ic)]])

    return {"universe_size": next_id, "sets": sets}
