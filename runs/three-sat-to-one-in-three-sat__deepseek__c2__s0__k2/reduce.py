"""Polynomial-time reduction from 3-SAT (SOURCE) to 1-in-3-SAT (TARGET).

SOURCE instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
TARGET instance: {"num_vars": M, "clauses": [[a, b, c], ...]}  (all positive)

Construction
------------
Global variable f is forced to be false by the gadget
    (f, a0, b0), (f, a0, c0), (a0, b0, c0)
whose only solution has f = 0, a0 = 1, b0 = c0 = 0.

For every source variable i we create a complementary pair (p_i, n_i) and the
clause (p_i, n_i, f), which (because f = 0) enforces p_i + n_i = 1.

For every source clause (l1, l2, l3) let a, b, c be the target variables for the
literals and abar, bbar, cbar their complements (the other variable of the
pair).  Introduce fresh y1..y6 and the clauses
    (abar, y1, y2), (bbar, y3, y4), (cbar, y5, y6), (y1, y3, y5).
The first three give y1 + y2 = a, y3 + y4 = b, y5 + y6 = c, so each yi can be 1
only when the corresponding literal is true.  The last clause requires exactly
one of y1, y3, y5 to be true, which is possible iff at least one of a, b, c is
true.  Hence the gadget is satisfiable exactly when the source clause is
satisfied.

The construction is linear in the size of the source instance.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    target_clauses = []
    counter = [0]

    def new_var():
        counter[0] += 1
        return counter[0]

    # --- global forced-false variable f and its gadget ---
    f = new_var()
    a0 = new_var()
    b0 = new_var()
    c0 = new_var()
    target_clauses.append([f, a0, b0])
    target_clauses.append([f, a0, c0])
    target_clauses.append([a0, b0, c0])

    # --- complementary pairs for the source variables ---
    pos = {}
    neg = {}
    for i in range(1, m + 1):
        p = new_var()
        n = new_var()
        pos[i] = p
        neg[i] = n
        target_clauses.append([p, n, f])

    def lit_var(lit):
        """Target variable representing the given source literal."""
        if lit > 0:
            return pos[lit]
        return neg[-lit]

    def lit_comp(lit):
        """Target variable representing the negation of the source literal."""
        if lit > 0:
            return neg[lit]
        return pos[-lit]

    # --- one OR gadget per source clause ---
    for cl in clauses:
        l1, l2, l3 = cl
        abar = lit_comp(l1)
        bbar = lit_comp(l2)
        cbar = lit_comp(l3)

        y1 = new_var()
        y2 = new_var()
        y3 = new_var()
        y4 = new_var()
        y5 = new_var()
        y6 = new_var()

        target_clauses.append([abar, y1, y2])
        target_clauses.append([bbar, y3, y4])
        target_clauses.append([cbar, y5, y6])
        target_clauses.append([y1, y3, y5])

    return {"num_vars": counter[0], "clauses": target_clauses}
