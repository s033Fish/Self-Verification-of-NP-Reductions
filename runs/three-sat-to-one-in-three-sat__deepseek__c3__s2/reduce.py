"""Polynomial-time reduction from 3-SAT (SOURCE) to 1-in-3-SAT (TARGET).

Idea
----
1-in-3-SAT only allows positive literals, so we simulate negation by giving
every source variable ``v`` two target variables: ``pos[v]`` meaning "v is
true" and ``neg[v]`` meaning "v is false".  A single variable ``f`` is forced
to be false, and the clause ``(pos[v], neg[v], f)`` then forces exactly one of
the pair to be true, i.e. ``neg[v] == not pos[v]``.

Forcing ``f`` false uses the 3-clause gadget
    (f, g1, g2), (f, g1, g3), (g1, g2, g3)
which is satisfiable with f = 0 but not with f = 1.

Each source clause (l1 or l2 or l3) becomes the 3-clause gadget
    (L1, a, b), (not L2, a, c), (not L3, b, d)
with fresh auxiliaries a, b, c, d, where Li is the target variable for li and
``not Li`` is its complement variable.  This gadget is satisfiable (over
a, b, c, d) exactly when L1 or L2 or L3 is true, so the whole target instance
is satisfiable iff the source formula is.

Everything is linear in the input size, so the reduction is polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a 3-SAT instance to a 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = 1

    def fresh():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    # A variable forced to be false.
    false_var = fresh()
    g1, g2, g3 = fresh(), fresh(), fresh()

    # Two target variables per source variable: one for the literal v, one
    # for its negation.
    pos = {}
    neg = {}
    for v in range(1, num_vars + 1):
        pos[v] = fresh()
        neg[v] = fresh()

    target_clauses = []

    # Force false_var == 0.
    target_clauses.append([false_var, g1, g2])
    target_clauses.append([false_var, g1, g3])
    target_clauses.append([g1, g2, g3])

    # Exactly one of pos[v], neg[v] is true.
    for v in range(1, num_vars + 1):
        target_clauses.append([pos[v], neg[v], false_var])

    def lit_var(literal):
        return pos[abs(literal)] if literal > 0 else neg[abs(literal)]

    def lit_complement(literal):
        return neg[abs(literal)] if literal > 0 else pos[abs(literal)]

    # One OR gadget per source clause.
    for l1, l2, l3 in clauses:
        a, b, c, d = fresh(), fresh(), fresh(), fresh()
        target_clauses.append([lit_var(l1), a, b])
        target_clauses.append([lit_complement(l2), a, c])
        target_clauses.append([lit_complement(l3), b, d])

    return {"num_vars": next_var - 1, "clauses": target_clauses}
