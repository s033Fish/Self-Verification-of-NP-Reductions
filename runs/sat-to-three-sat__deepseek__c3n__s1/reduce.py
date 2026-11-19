"""Polynomial-time reduction from SAT to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
Target instance: {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

Strategy
--------
1. Normalise every source clause:
     * remove repeated literals;
     * if it contains both v and -v it is a tautology, so drop it;
     * a clause that becomes empty makes the formula unsatisfiable.
2. Encode each remaining clause of length k with auxiliary variables:
     * k == 1: force the literal true with a 4-clause gadget over 2 aux vars.
     * k == 2: pad with 1 aux var (l1 v l2 v a) and (l1 v l2 v -a).
     * k == 3: keep the clause as is.
     * k >= 4: standard Tseitin chain using k-3 aux vars.
   All produced clauses have exactly 3 literals on 3 distinct variables.
3. If the source is unsatisfiable (empty clause present) emit a fixed
   unsatisfiable gadget (all eight 3-clauses) over 3 fresh variables.

Auxiliary variables are numbered m+1, m+2, ... so the result is always a
valid 3-SAT instance.  The encoding is answer-preserving because the aux
variables are existentially quantified and each gadget is satisfiable for
exactly the assignments that satisfy the original clause.
"""

from __future__ import annotations


def _clean(clause):
    """Deduplicate literals; return None if the clause is a tautology."""
    seen = set()
    result = []
    for lit in clause:
        if -lit in seen:
            return None  # tautology: always satisfied, drop it
        if lit not in seen:
            seen.add(lit)
            result.append(lit)
    return result


def _unsat_gadget(start):
    """All eight 3-clauses over fresh vars start, start+1, start+2.

    Every assignment of the three variables falsifies exactly one of the
    eight clauses, so the conjunction is unsatisfiable.
    """
    a, b, c = start, start + 1, start + 2
    clauses = []
    for sa in (a, -a):
        for sb in (b, -b):
            for sc in (c, -c):
                clauses.append([sa, sb, sc])
    return clauses


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    cleaned = []
    for clause in clauses:
        normalised = _clean(clause)
        if normalised is None:
            continue
        cleaned.append(normalised)

    # An empty clause can never be satisfied.
    if any(len(c) == 0 for c in cleaned):
        return {"num_vars": m + 3, "clauses": _unsat_gadget(m + 1)}

    next_var = m + 1
    out = []

    for clause in cleaned:
        k = len(clause)
        if k == 1:
            (lit,) = clause
            a, b = next_var, next_var + 1
            next_var += 2
            out.append([lit, a, b])
            out.append([lit, a, -b])
            out.append([lit, -a, b])
            out.append([lit, -a, -b])
        elif k == 2:
            l1, l2 = clause
            a = next_var
            next_var += 1
            out.append([l1, l2, a])
            out.append([l1, l2, -a])
        elif k == 3:
            out.append([clause[0], clause[1], clause[2]])
        else:
            ys = list(range(next_var, next_var + (k - 3)))
            next_var += k - 3
            out.append([clause[0], clause[1], ys[0]])
            for i in range(1, k - 3):
                out.append([-ys[i - 1], clause[i + 1], ys[i]])
            out.append([-ys[k - 4], clause[k - 2], clause[k - 1]])

    return {"num_vars": next_var - 1, "clauses": out}
