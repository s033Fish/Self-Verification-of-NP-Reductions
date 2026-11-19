"""Polynomial-time reduction from positive 1-in-3-SAT to Exact Cover.

Construction
------------
For each variable i (1..m) we create a selector element s_i.
For every occurrence of variable i in a clause we create an element n_i^j.
For every clause k we create a clause element c_k.

Variable gadget (for variable i):
    T_i = {s_i}                       (meaning x_i is true)
    F_i = {s_i} + all n_i^j           (meaning x_i is false)

Exactly one of T_i, F_i must be chosen to cover s_i.  If T_i is chosen, every
n_i^j is left uncovered and therefore must be covered by a clause gadget; if
F_i is chosen, all n_i^j are already covered and no clause gadget for variable
i can be used.

Clause gadget (for clause k = (a, b, c)):
    for each variable v in the clause, the set {n_v^j, c_k}, where j is the
    occurrence of v in clause k.

The clause element c_k can only be covered by choosing {n_v^j, c_k} for some v
in the clause.  Such a set can be chosen only when n_v^j is uncovered, i.e.
only when x_v is true.  Hence every clause needs at least one true variable.
If a clause had two true variables, both corresponding n elements would be
uncovered and would each require their own clause set, but those two sets both
contain c_k and overlap; exact cover forbids that.  So every clause has exactly
one true variable.

Conversely, an assignment with exactly one true variable per clause yields an
exact cover by choosing T_i for true variables, F_i for false variables, and
for each clause the unique set belonging to its true variable.

The reduction is linear in the size of the input.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # Elements 0 .. num_vars-1 are the selector elements s_i.
    next_element = num_vars

    # occurrence_elements[i] collects the elements n_i^j, one per occurrence
    # of variable i (source variables are 1-based).
    occurrence_elements = [[] for _ in range(num_vars)]
    clause_occurrences = []
    for clause in clauses:
        occurrence_ids = []
        for var in clause:
            i = var - 1
            element = next_element
            next_element += 1
            occurrence_elements[i].append(element)
            occurrence_ids.append(element)
        clause_occurrences.append(occurrence_ids)

    # One clause element c_k per clause.
    clause_elements = []
    for _ in range(n):
        clause_elements.append(next_element)
        next_element += 1

    universe_size = next_element
    sets = []

    # Variable gadgets.
    for i in range(num_vars):
        sets.append([i])
        sets.append([i] + occurrence_elements[i])

    # Clause gadgets.
    for k in range(n):
        c = clause_elements[k]
        for occurrence in clause_occurrences[k]:
            sets.append([occurrence, c])

    return {"universe_size": universe_size, "sets": sets}
