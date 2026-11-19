"""Polynomial-time reduction from 3-SAT to Exact Cover.

Construction
------------
Let the formula have variables 1..m and clauses C_1..C_k.

Universe elements
  * For every variable v: one element e_v.
  * For every *occurrence* of a literal in a clause: one element.  An
    occurrence of the positive literal v gets a "positive copy" of v; an
    occurrence of the negative literal ~v gets a "negative copy" of v.
  * For every clause C_j: one element c_j.

Sets
  * Variable gadget for v:
        A_v = {e_v} u {positive copies of v}     (meaning "v is FALSE")
        B_v = {e_v} u {negative copies of v}     (meaning "v is TRUE")
    The element e_v occurs only in A_v and B_v, so an exact cover chooses
    exactly one of them.  If A_v is chosen every positive copy of v is
    covered and every negative copy stays free; if B_v is chosen the roles
    swap.  Hence exactly the copies of one polarity are available to clauses.
  * For every literal occurrence, a singleton set containing its copy.  These
    absorb copies that no clause ends up using (they are optional, so they do
    not force anything).
  * For every clause C_j and every literal occurrence l in it, the set
        {c_j, copy(l)}.
    The element c_j occurs only in these sets, so exactly one is chosen, and
    it can be chosen exactly when copy(l) is still uncovered, i.e. when the
    literal l is TRUE under the assignment encoded by the gadgets.

A satisfying assignment yields an exact cover (choose the gadget matching the
assignment, one clause set per clause for a true literal, singletons for the
remaining copies).  Conversely any exact cover encodes a consistent
assignment in which every clause has a true literal.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    sets: list[list[int]] = []
    next_elem = 0

    # One element e_v per variable.
    e = {}
    for v in range(1, num_vars + 1):
        e[v] = next_elem
        next_elem += 1

    pos_copies: dict[int, list[int]] = {v: [] for v in range(1, num_vars + 1)}
    neg_copies: dict[int, list[int]] = {v: [] for v in range(1, num_vars + 1)}
    clause_sets: list[list[int]] = []

    # One element per literal occurrence, plus one element per clause.
    for clause in clauses:
        c = next_elem
        next_elem += 1
        for literal in clause:
            copy = next_elem
            next_elem += 1
            v = abs(literal)
            if literal > 0:
                pos_copies[v].append(copy)
            else:
                neg_copies[v].append(copy)
            clause_sets.append([c, copy])

    # Variable gadgets.
    for v in range(1, num_vars + 1):
        sets.append([e[v]] + pos_copies[v])  # A_v: v FALSE
        sets.append([e[v]] + neg_copies[v])  # B_v: v TRUE

    # Singletons absorbing unused copies.
    for v in range(1, num_vars + 1):
        for copy in pos_copies[v]:
            sets.append([copy])
        for copy in neg_copies[v]:
            sets.append([copy])

    # Clause gadgets.
    sets.extend(clause_sets)

    return {"universe_size": next_elem, "sets": sets}
