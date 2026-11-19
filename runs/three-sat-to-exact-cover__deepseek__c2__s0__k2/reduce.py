"""Polynomial-time reduction from 3-SAT to Exact Cover.

Source instance (ThreeSat):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Variables are 1..m; a literal is +v or -v; each clause has exactly three
    literals on three different variables.

Target instance (ExactCover):
    {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Universe elements:
    * a_i          for each variable i = 1..m          (index i-1)
    * C_j          for each clause j                   (index m + j)
    * o_{j,k}      for each literal occurrence (clause j, position k)
                   (index m + n + 3*j + k)

Sets:
    * For each variable v:
        TrueSet_v  = {a_v} u {o_{j,k} : literal at (j,k) is -v}
        FalseSet_v = {a_v} u {o_{j,k} : literal at (j,k) is +v}
      Since a_v occurs only in these two sets and must be covered exactly
      once, exactly one is chosen.  Choosing TrueSet_v covers all occurrences
      of -v, leaving occurrences of +v free; choosing FalseSet_v does the
      opposite.  So the chosen set covers exactly the occurrences of the
      literal that is FALSE.
    * For each clause j and each position k:
        {C_j, o_{j,k}}
      C_j occurs only in these sets, so exactly one is chosen per clause.
      Such a set can be selected only when o_{j,k} is still free, i.e. only
      when the literal at (j,k) is TRUE.
    * For each occurrence (j,k): the singleton {o_{j,k}}, which covers
      occurrences of true literals that their clause did not select.

Correctness
-----------
(=>) Given a satisfying assignment, choose TrueSet_v or FalseSet_v according
to the truth value of v.  For every clause pick one true literal and select
its clause set; cover every remaining occurrence with its singleton.  This
covers every element exactly once.

(<=) Given an exact cover, a_v is covered exactly once, so exactly one of
TrueSet_v / FalseSet_v is chosen; this defines an assignment.  Each C_j is
covered by exactly one clause set {C_j, o_{j,k}}.  That set is disjoint from
the chosen variable set, which forces the literal at (j,k) to be true under
the assignment.  Hence every clause is satisfied.

The construction uses u = m + 4n elements and 2m + 6n sets, so it runs in
polynomial time.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    n = len(clauses)

    universe_size = m + 4 * n

    def clause_elem(j):
        return m + j

    def occ_elem(j, k):
        return m + n + 3 * j + k

    # Occurrence elements grouped by the sign of the literal they belong to.
    pos = [[] for _ in range(m + 1)]  # pos[v]: occurrences of +v
    neg = [[] for _ in range(m + 1)]  # neg[v]: occurrences of -v
    for j, clause in enumerate(clauses):
        for k, lit in enumerate(clause):
            v = abs(lit)
            if lit > 0:
                pos[v].append(occ_elem(j, k))
            else:
                neg[v].append(occ_elem(j, k))

    sets = []

    # Variable gadgets: exactly one of the two sets per variable is chosen.
    for v in range(1, m + 1):
        a = v - 1
        sets.append([a] + neg[v])  # v is TRUE
        sets.append([a] + pos[v])  # v is FALSE

    # Clause gadgets: exactly one literal occurrence per clause is selected.
    for j, clause in enumerate(clauses):
        ce = clause_elem(j)
        for k in range(len(clause)):
            sets.append([ce, occ_elem(j, k)])

    # Singletons cover occurrences of true literals not selected by a clause.
    for j, clause in enumerate(clauses):
        for k in range(len(clause)):
            sets.append([occ_elem(j, k)])

    return {"universe_size": universe_size, "sets": sets}
