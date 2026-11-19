"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
Target instance: {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

Each source clause is replaced by a small 3-CNF over the original
variables plus fresh auxiliary variables, such that the whole target
formula is satisfiable iff the source formula is satisfiable.

Clause handling (after canonicalisation):
  * A clause containing both v and -v is a tautology and is dropped.
  * Repeated literals are removed.
  * Empty clause  -> an unsatisfiable 8-clause gadget on 3 fresh vars.
  * 1 literal     -> 4 clauses using 2 fresh vars (forces that literal).
  * 2 literals    -> 2 clauses using 1 fresh var.
  * 3 literals    -> used directly (they are on 3 distinct variables).
  * k >= 4        -> standard chain using k-3 fresh vars.

All fresh variables are numbered above the source's num_vars, so the
target instance is always a valid 3-SAT instance.
"""


def _unsat_gadget(base):
    """Return (clauses, next_var) for an unsatisfiable 3-CNF on 3 fresh vars.

    `base` is the first fresh variable number.  The eight clauses over
    (a, b, c) are unsatisfiable.
    """
    a, b, c = base, base + 1, base + 2
    clauses = [
        [a, b, c],
        [a, b, -c],
        [a, -b, c],
        [a, -b, -c],
        [-a, b, c],
        [-a, b, -c],
        [-a, -b, c],
        [-a, -b, -c],
    ]
    return clauses, base + 3


def reduce(instance):
    num_vars = instance["num_vars"]
    src_clauses = instance["clauses"]

    next_var = num_vars + 1

    def new_var():
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    out = []

    for clause in src_clauses:
        # Canonicalise: keep one sign per variable, detect tautologies.
        signs = {}          # var -> +1 / -1
        order = []          # variables in first-seen order
        tautology = False
        for lit in clause:
            var = abs(lit)
            sign = 1 if lit > 0 else -1
            if var in signs:
                if signs[var] != sign:
                    tautology = True
                    break
            else:
                signs[var] = sign
                order.append(var)

        if tautology:
            # Always true: contributes nothing.
            continue

        lits = [signs[var] * var for var in order]
        k = len(lits)

        if k == 0:
            # Empty clause: the source is unsatisfiable.  Emit an
            # unsatisfiable 3-SAT formula and stop.
            clauses, _ = _unsat_gadget(1)
            return {"num_vars": 3, "clauses": clauses}

        if k == 1:
            l1 = lits[0]
            p = new_var()
            q = new_var()
            out.append([l1, p, q])
            out.append([l1, p, -q])
            out.append([l1, -p, q])
            out.append([l1, -p, -q])

        elif k == 2:
            l1, l2 = lits
            p = new_var()
            out.append([l1, l2, p])
            out.append([l1, l2, -p])

        elif k == 3:
            out.append([lits[0], lits[1], lits[2]])

        else:
            # k >= 4: chain encoding.
            ys = [new_var() for _ in range(k - 3)]
            out.append([lits[0], lits[1], ys[0]])
            for j in range(1, k - 3):
                out.append([-ys[j - 1], lits[j + 1], ys[j]])
            out.append([-ys[k - 4], lits[k - 2], lits[k - 1]])

    return {"num_vars": next_var - 1, "clauses": out}
