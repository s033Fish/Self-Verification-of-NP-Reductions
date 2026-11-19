"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Source instance (1-in-3-SAT):
    {"num_vars": m, "clauses": [[a, b, c], ...]}

Target instance (Exact Cover):
    {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Let n be the number of clauses.

Universe elements:
  * 0 .. n-1          one "clause element" per clause.
  * n .. n+3n-1       one "copy" element per occurrence of a variable in a
                      clause (there are exactly 3 occurrences per clause).

Sets:
  * For every variable x, the set F_x consisting of all copies of x.
    Selecting F_x means "x is false": it covers every copy of x, so no
    clause set that uses x can be selected.
  * For every clause j = (a, b, c) and every position k in {0,1,2}, the
    set {j, copy(j, k)}.  Selecting it means "the k-th variable of clause j
    is the unique true variable of that clause".

Correctness
-----------
(=>) Given a satisfying assignment, pick for each clause the set of its
unique true variable, and pick F_x for every false variable.  Every clause
element is covered once, every copy of a true variable is covered by the
clause set that selected it, and every copy of a false variable is covered
by F_x.  The chosen sets are pairwise disjoint, so this is an exact cover.

(<=) Given an exact cover, each clause element is covered by exactly one of
its three clause sets, giving exactly one true variable per clause.  For a
variable x, either F_x is selected (then no clause set using x is selected,
so x is false in every clause containing it), or F_x is not selected (then
all copies of x must be covered by clause sets, so every clause containing
x selects x, i.e. x is true in every such clause).  Hence the induced
assignment is well defined and satisfies exactly one literal per clause.

The construction is linear in the input size, hence polynomial time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # Element numbering: 0..n-1 are clause elements, then one element per
    # occurrence of a variable in a clause.
    next_element = n

    # copy_index[j][k] is the universe element for the k-th variable of
    # clause j; copies[x] collects all copy elements belonging to variable x.
    copy_index = []
    copies = {x: [] for x in range(1, num_vars + 1)}

    for clause in clauses:
        row = []
        for x in clause:
            element = next_element
            next_element += 1
            row.append(element)
            copies[x].append(element)
        copy_index.append(row)

    universe_size = next_element
    sets = []

    # One set per variable, covering all of its occurrence copies.
    for x in range(1, num_vars + 1):
        sets.append(list(copies[x]))

    # One set per (clause, variable) pair: the clause element plus that
    # variable's copy for this occurrence.
    for j, clause in enumerate(clauses):
        for k in range(len(clause)):
            sets.append([j, copy_index[j][k]])

    return {"universe_size": universe_size, "sets": sets}
