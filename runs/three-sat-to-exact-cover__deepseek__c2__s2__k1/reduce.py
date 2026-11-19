"""Polynomial-time reduction from 3-SAT to Exact Cover.

Construction
------------
Let the 3-SAT instance have variables 1..m and clauses C_0..C_{n-1}.

Universe elements
  * e_v        for each variable v (1..m)          -> id v-1
  * c_j        for each clause j                    -> id m+j
  * occ(j,k)   for each clause j and position k     -> id m+n+3*j+k

Sets
  * A_v = {e_v} U { occ(j,k) : literal (j,k) == -v }   ("v is true")
  * B_v = {e_v} U { occ(j,k) : literal (j,k) ==  v }   ("v is false")
  * for every clause j and position k:
        {c_j, occ(j,k)}      (clause set: selects a satisfying literal)
        {occ(j,k)}           (singleton: covers a true occurrence not selected)

A_v and B_v share e_v, so exactly one of them is chosen, which encodes the
truth value of v.  A chosen variable set covers exactly the occurrences of
the *false* literal of v.  Hence a clause set {c_j, occ(j,k)} can be chosen
only when literal (j,k) is true, and c_j must be covered by such a set.
Conversely, a satisfying assignment yields an exact cover: pick one
variable set per variable, one clause set per clause for a true literal, and
singletons for the remaining true occurrences.

The instance has m + 4n elements and 2m + 6n sets, so the reduction is
polynomial and does not solve either problem.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    n = len(clauses)

    universe_size = m + 4 * n

    def e_id(v):
        return v - 1

    def c_id(j):
        return m + j

    def occ_id(j, k):
        return m + n + 3 * j + k

    sets = []

    # Variable gadgets.
    for v in range(1, m + 1):
        true_set = [e_id(v)]    # chosen when v is true; covers -v occurrences
        false_set = [e_id(v)]   # chosen when v is false; covers +v occurrences
        for j, clause in enumerate(clauses):
            for k, literal in enumerate(clause):
                if literal == -v:
                    true_set.append(occ_id(j, k))
                elif literal == v:
                    false_set.append(occ_id(j, k))
        sets.append(true_set)
        sets.append(false_set)

    # Clause gadgets.
    for j, clause in enumerate(clauses):
        for k in range(len(clause)):
            sets.append([c_id(j), occ_id(j, k)])
            sets.append([occ_id(j, k)])

    return {"universe_size": universe_size, "sets": sets}
