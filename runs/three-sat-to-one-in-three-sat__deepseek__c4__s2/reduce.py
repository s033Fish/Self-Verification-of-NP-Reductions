"""Polynomial-time reduction from 3-SAT to positive 1-in-3-SAT.

Gadgets (all clauses are positive 1-in-3 clauses):

Negation gadget, for a source variable v with fresh vars nv,a0,a1,a2:
    {v, nv, a0}, {v, nv, a1}, {a0, a1, a2}
This is satisfiable iff nv == not v (verified by exhaustive search).

Clause gadget, for a source clause with mapped variables M1,M2,M3 and fresh
vars a0,a1,a2,a3:
    {comp(M1), a0, a1}, {comp(M2), a2, a3}, {M3, a0, a2}
This is satisfiable iff at least one of M1,M2,M3 is true (verified by
exhaustive search).  comp(X) is the complement variable of X, available
because every source variable v has both v and its negation variable nv.

Each source literal l is mapped to the target variable v (if l = +v) or nv
(if l = -v).  Then a source clause is satisfiable exactly when its gadget is.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    m = instance["num_vars"]
    clauses = instance["clauses"]

    out_clauses = []
    next_var = m + 1
    neg = {}  # source var v -> target variable representing not v

    # Negation gadgets: force neg[v] == not v.
    for v in range(1, m + 1):
        nv = next_var
        a0 = next_var + 1
        a1 = next_var + 2
        a2 = next_var + 3
        next_var += 4
        neg[v] = nv
        out_clauses.append([v, nv, a0])
        out_clauses.append([v, nv, a1])
        out_clauses.append([a0, a1, a2])

    # complement map for every target variable used as a mapped literal:
    # v <-> neg[v], and neg[v] <-> v.
    comp_map = {}
    for v in range(1, m + 1):
        comp_map[v] = neg[v]
        comp_map[neg[v]] = v

    def comp(var: int) -> int:
        return comp_map[var]

    # Clause gadgets: one per source clause.
    for clause in clauses:
        mapped = []
        for lit in clause:
            v = abs(lit)
            mapped.append(v if lit > 0 else neg[v])
        a0 = next_var
        a1 = next_var + 1
        a2 = next_var + 2
        a3 = next_var + 3
        next_var += 4
        out_clauses.append([comp(mapped[0]), a0, a1])
        out_clauses.append([comp(mapped[1]), a2, a3])
        out_clauses.append([mapped[2], a0, a2])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
