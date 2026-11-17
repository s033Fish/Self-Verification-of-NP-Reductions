"""Polynomial-time reduction from 3-SAT to Exact Cover.

Given a 3-SAT instance with variables 1..m and clauses C_0..C_{n-1}, we build
an Exact Cover instance as follows.

Elements
    * s_v            selector element for variable v (v = 1..m)
    * c_j            element for clause j
    * copy[j][k]     element for the k-th literal occurrence of clause j

Sets
    * variable gadget, for each v:
          {s_v} U {copy[j][k] : literal of clause j at k is -v}   (v true)
          {s_v} U {copy[j][k] : literal of clause j at k is +v}   (v false)
      The two sets share s_v, so an exact cover chooses exactly one of them.
      Choosing "v true" covers every copy of the literal -v, leaving the
      copies of +v free for clauses (and symmetrically for "v false").
    * singleton {copy[j][k]} for every literal occurrence, used to cover a
      true literal's copy that no clause consumes.
    * clause gadget {c_j, copy[j][k]} for every occurrence.  c_j must be
      covered by exactly one of these, and that is possible only when the
      occurrence's literal is true (its copy is then not covered by the
      variable gadget).

Hence an exact cover exists exactly when some assignment satisfies every
clause, and the construction uses O(m + n) elements and sets.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    num_clauses = len(clauses)

    # Assign universe element ids.
    next_id = 0

    selector = {}
    for v in range(1, num_vars + 1):
        selector[v] = next_id
        next_id += 1

    clause_element = []
    for _ in range(num_clauses):
        clause_element.append(next_id)
        next_id += 1

    # copy_element[j][k] is the element for the k-th literal of clause j.
    copy_element = []
    for _ in range(num_clauses):
        row = []
        for _ in range(3):
            row.append(next_id)
            next_id += 1
        copy_element.append(row)

    # Group copy elements by the literal they represent.
    positive_copies = {v: [] for v in range(1, num_vars + 1)}
    negative_copies = {v: [] for v in range(1, num_vars + 1)}
    for j in range(num_clauses):
        for k in range(3):
            literal = clauses[j][k]
            v = abs(literal)
            if literal > 0:
                positive_copies[v].append(copy_element[j][k])
            else:
                negative_copies[v].append(copy_element[j][k])

    sets = []

    # Variable gadget.
    for v in range(1, num_vars + 1):
        sets.append([selector[v]] + negative_copies[v])  # v is true
        sets.append([selector[v]] + positive_copies[v])  # v is false

    # A copy not consumed by a clause can be covered on its own.
    for j in range(num_clauses):
        for k in range(3):
            sets.append([copy_element[j][k]])

    # Clause gadget.
    for j in range(num_clauses):
        for k in range(3):
            sets.append([clause_element[j], copy_element[j][k]])

    return {"universe_size": next_id, "sets": sets}
