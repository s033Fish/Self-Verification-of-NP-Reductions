"""Polynomial-time reduction from 3-SAT to positive 1-in-3-SAT.

Target variable layout:
    1 .. m        : positive copy of source variable v
    m+1 .. 2m     : negative copy of source variable v  (m+v)
    2m+1          : F, a variable forced to be false
    remaining     : fresh auxiliary variables used by the gadgets

Gadgets (all clauses are positive 1-in-3 clauses, i.e. exactly one true):
  * Constant false: (F,a,b),(F,c,d),(F,e,f),(a,c,e) forces F=0.
  * Negation:       (v, m+v, F) with F=0 forces m+v = NOT v.
  * Clause:         (n1,a,b),(n2,c,d),(n3,e,f),(a,c,e) is satisfiable
                    iff not all of n1,n2,n3 are true.
For a source clause we set n_i = NOT(literal_i), so the clause gadget is
satisfiable exactly when at least one literal of the source clause is true.
"""


def reduce(instance):
    m = instance["num_vars"]
    src_clauses = instance["clauses"]

    num_vars = 2 * m + 1
    F = 2 * m + 1  # variable forced to false

    clauses = []

    def fresh():
        nonlocal num_vars
        num_vars += 1
        return num_vars

    # Gadget forcing F = 0 (false).
    a, b, c, d, e, f = fresh(), fresh(), fresh(), fresh(), fresh(), fresh()
    clauses.append([F, a, b])
    clauses.append([F, c, d])
    clauses.append([F, e, f])
    clauses.append([a, c, e])

    # Negation gadgets: m+v represents NOT v.
    for v in range(1, m + 1):
        clauses.append([v, m + v, F])

    # One gadget per source clause.
    for clause in src_clauses:
        ns = []
        for lit in clause:
            if lit > 0:
                ns.append(m + lit)   # NOT (+v) = v_bar
            else:
                ns.append(-lit)      # NOT (-v) = v
        n1, n2, n3 = ns
        a, b, c, d, e, f = fresh(), fresh(), fresh(), fresh(), fresh(), fresh()
        clauses.append([n1, a, b])
        clauses.append([n2, c, d])
        clauses.append([n3, e, f])
        clauses.append([a, c, e])

    return {"num_vars": num_vars, "clauses": clauses}
