"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

SOURCE (OneInThreeSat): {"num_vars": m, "clauses": [[a, b, c], ...]}
TARGET (ExactCover):    {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Elements
  * one selector element s_v for every variable v in 1..m;
  * one port element p_{v,C} for every occurrence of variable v in clause C;
  * one clause element e_C for every clause C.

Sets
  * variable gadget for v (let P_v be the set of its port elements):
        {s_v}            -- choosing it means v is TRUE  (ports stay free)
        {s_v} | P_v      -- choosing it means v is FALSE (ports get covered)
    s_v must be covered exactly once, so exactly one of the two is chosen.
  * clause gadget for clause C = (a, b, c):
        {p_{a,C}, e_C}, {p_{b,C}, e_C}, {p_{c,C}, e_C}
    e_C must be covered exactly once, so exactly one of the three sets is
    chosen; that set can only be used when the corresponding port is free,
    i.e. when that variable is TRUE.

Hence exact covers correspond bijectively to assignments in which every
clause has exactly one true variable.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    next_id = 0

    def new_element():
        nonlocal next_id
        element = next_id
        next_id += 1
        return element

    # Selector element for each variable.
    selector = {v: new_element() for v in range(1, num_vars + 1)}

    # Clause elements and one port element per variable occurrence.
    clause_element = []
    port = {}          # (variable, clause_index) -> element
    occurrences = {v: [] for v in range(1, num_vars + 1)}
    for ci, clause in enumerate(clauses):
        clause_element.append(new_element())
        for v in clause:
            p = new_element()
            port[(v, ci)] = p
            occurrences[v].append(p)

    sets = []

    # Variable gadgets.
    for v in range(1, num_vars + 1):
        sets.append([selector[v]])
        sets.append([selector[v]] + occurrences[v])

    # Clause gadgets.
    for ci, clause in enumerate(clauses):
        for v in clause:
            sets.append([port[(v, ci)], clause_element[ci]])

    return {"universe_size": next_id, "sets": sets}
