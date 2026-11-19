"""Polynomial-time reduction from 3-SAT (SOURCE) to 1-in-3-SAT (TARGET).

Encoding
--------
For every source variable v we create two target variables:
    T_v  (intended meaning: v is true)
    F_v  (intended meaning: v is false)
and enforce T_v != F_v with a small positive 1-in-3 gadget on 4 variables
(2 inputs + 2 fresh auxiliaries is impossible; 2 inputs + 3 auxiliaries works):

    (T_v, F_v, a)
    (T_v, F_v, b)
    (a, b, c)

This formula is satisfiable exactly when T_v != F_v.

For every source clause (l1, l2, l3) we use the positive 1-in-3 gadget
(3 inputs + 4 fresh auxiliaries) that is satisfiable iff the OR of its three
logical inputs is true.  Written with a variable X standing for the negation
of an input, the gadget is

    (v0, a, b)
    (X1, a, c)
    (X2, b, d)

which is satisfiable iff v0 OR v1 OR v2.  We feed
    v0 = rep(l1),  X1 = comp_rep(l2),  X2 = comp_rep(l3)
where rep(+v) = T_v, rep(-v) = F_v and comp_rep(l) is the target variable
representing the complement of literal l.  Since T_v and F_v are forced to be
complementary, the gadget is satisfiable iff rep(l1) OR rep(l2) OR rep(l3),
i.e. exactly when the source clause is satisfied.

The gadgets only share the T_v / F_v variables, so the whole target instance
is satisfiable iff the source instance is.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Variable numbering for the target instance.
    T: dict[int, int] = {}
    F: dict[int, int] = {}
    next_var = 1
    for v in range(1, m + 1):
        T[v] = next_var
        next_var += 1
        F[v] = next_var
        next_var += 1

    def rep(lit: int) -> int:
        """Target variable representing the truth value of literal lit."""
        if lit > 0:
            return T[lit]
        return F[-lit]

    def comp_rep(lit: int) -> int:
        """Target variable representing the negation of literal lit."""
        if lit > 0:
            return F[lit]
        return T[-lit]

    out_clauses: list[list[int]] = []

    # Consistency gadgets: T_v != F_v.
    for v in range(1, m + 1):
        a = next_var
        next_var += 1
        b = next_var
        next_var += 1
        c = next_var
        next_var += 1
        out_clauses.append([T[v], F[v], a])
        out_clauses.append([T[v], F[v], b])
        out_clauses.append([a, b, c])

    # Clause gadgets: one per source clause.
    for clause in clauses:
        l1, l2, l3 = clause
        a = next_var
        next_var += 1
        b = next_var
        next_var += 1
        c = next_var
        next_var += 1
        d = next_var
        next_var += 1
        out_clauses.append([rep(l1), a, b])
        out_clauses.append([comp_rep(l2), a, c])
        out_clauses.append([comp_rep(l3), b, d])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
