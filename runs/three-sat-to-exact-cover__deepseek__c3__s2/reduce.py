"""Polynomial-time reduction from 3-SAT (ThreeSat) to Exact Cover (ExactCover).

Instance formats (see problems.py):

  ThreeSat:   {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
  ExactCover: {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Let the formula have m variables and n clauses.

Universe elements:
  * e_i                for each variable i = 1..m      (forces a truth value)
  * c_j                for each clause j = 0..n-1      (must be satisfied)
  * f_{j,k}            for each clause j and literal position k in {0,1,2}

Sets:
  * For each variable i:
      T_i = {e_i} u { f_{j,k} : literal (j,k) is -i }   ("x_i is true")
      F_i = {e_i} u { f_{j,k} : literal (j,k) is +i }   ("x_i is false")
    Both contain e_i, so exactly one is chosen; it covers e_i and the
    f-elements of the literals that become FALSE under this choice.
  * For each clause j and position k:
      {c_j, f_{j,k}}   (usable only when literal (j,k) is true)
      {f_{j,k}}        (absorbs f-elements of true literals not used to
                        satisfy their clause)

Correctness: c_j can only be covered by some {c_j, f_{j,k}}, which requires
f_{j,k} to be uncovered, i.e. literal (j,k) true.  Conversely a satisfying
assignment lets us pick one true literal per clause for {c_j, f_{j,k}} and
cover every other true literal's f-element by its singleton.
"""


def reduce(instance):
    """Return an Exact Cover instance that is yes iff `instance` (3-SAT) is yes."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # Element index layout.
    def e(i):          # variable i (1-based) -> index
        return i - 1

    def c(j):          # clause j (0-based) -> index
        return num_vars + j

    def f(j, k):       # clause j, literal position k -> index
        return num_vars + n + 3 * j + k

    universe_size = num_vars + 4 * n
    sets = []

    # Variable gadgets: exactly one of T_i / F_i is chosen.
    for i in range(1, num_vars + 1):
        positive = []  # f-elements of clauses where +i occurs (false if x_i true)
        negative = []  # f-elements of clauses where -i occurs (false if x_i false)
        for j, clause in enumerate(clauses):
            for k, literal in enumerate(clause):
                if literal == i:
                    positive.append(f(j, k))
                elif literal == -i:
                    negative.append(f(j, k))
        sets.append([e(i)] + negative)  # T_i
        sets.append([e(i)] + positive)  # F_i

    # Clause gadgets.
    for j in range(n):
        for k in range(3):
            sets.append([c(j), f(j, k)])
            sets.append([f(j, k)])

    return {"universe_size": universe_size, "sets": sets}
