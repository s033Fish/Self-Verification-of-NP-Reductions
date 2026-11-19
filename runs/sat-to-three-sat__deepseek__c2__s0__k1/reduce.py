"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

reduce(instance) takes a Sat instance {"num_vars": m, "clauses": [...]}
and returns a ThreeSat instance {"num_vars": M, "clauses": [...]} that is
satisfiable exactly when the input is.

Construction
------------
Normalise every input clause: remove duplicate literals and drop clauses
containing both v and -v (tautologies, always true).  A clause that is
empty after normalisation (i.e. the input empty clause) makes the formula
unsatisfiable; we then return a fixed unsatisfiable 3-CNF on 3 fresh vars.

Otherwise each normalised clause has k >= 1 literals on k distinct
variables:

  k = 1 : (l1 v p v q)
  k = 2 : (l1 v l2 v p)
  k = 3 : (l1 v l2 v l3)
  k >= 4: (l1 v l2 v y1), (-y1 v l3 v y2), ..., (-y_{k-3} v l_{k-1} v lk)

where p, q are fresh variables forced to false by the gadget

  (-p v a v b), (-p v -a v b), (-p v a v -b), (-p v -a v -b)

(and likewise for q).  With p = q = false the short-clause encodings are
exactly the original clauses, so the reduction preserves satisfiability in
both directions.  All fresh variables are distinct and greater than m.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = num_vars + 1

    def fresh():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    # --- normalise clauses: dedupe literals, drop tautologies -------------
    normalized = []
    for clause in clauses:
        seen = set()
        lits = []
        for lit in clause:
            if lit not in seen:
                seen.add(lit)
                lits.append(lit)
        if any(-lit in seen for lit in lits):
            continue  # tautology: always satisfiable, safe to drop
        if not lits:
            # Empty clause: the input is unsatisfiable.  Emit the eight
            # clauses over three fresh variables, which is unsatisfiable.
            a, b, c = fresh(), fresh(), fresh()
            out = []
            for sa in (1, -1):
                for sb in (1, -1):
                    for sc in (1, -1):
                        out.append([sa * a, sb * b, sc * c])
            return {"num_vars": next_var - 1, "clauses": out}
        normalized.append(lits)

    # --- forced-false padding variables, only if short clauses exist ------
    need_pad = any(len(lits) < 3 for lits in normalized)
    p = q = None
    out_clauses = []
    if need_pad:
        p, q, a, b = fresh(), fresh(), fresh(), fresh()
        # force p = false
        out_clauses.append([-p, a, b])
        out_clauses.append([-p, -a, b])
        out_clauses.append([-p, a, -b])
        out_clauses.append([-p, -a, -b])
        # force q = false
        out_clauses.append([-q, a, b])
        out_clauses.append([-q, -a, b])
        out_clauses.append([-q, a, -b])
        out_clauses.append([-q, -a, -b])

    # --- encode each clause as 3-clauses ---------------------------------
    for lits in normalized:
        k = len(lits)
        if k == 1:
            out_clauses.append([lits[0], p, q])
        elif k == 2:
            out_clauses.append([lits[0], lits[1], p])
        elif k == 3:
            out_clauses.append([lits[0], lits[1], lits[2]])
        else:
            ys = [fresh() for _ in range(k - 3)]
            out_clauses.append([lits[0], lits[1], ys[0]])
            for i in range(1, k - 3):
                out_clauses.append([-ys[i - 1], lits[i + 1], ys[i]])
            out_clauses.append([-ys[-1], lits[k - 2], lits[k - 1]])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
