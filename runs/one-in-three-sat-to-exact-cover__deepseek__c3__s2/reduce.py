"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Idea
----
A 1-in-3-SAT assignment is just the set of variables declared true, subject to
the condition that every clause contains exactly one true variable.

Build an Exact Cover instance whose universe is the set of clause indices
0..n-1.  For every variable x create one set S_x consisting of the indices of
the clauses in which x occurs.  Choosing S_x corresponds to setting x true.

A sub-collection of the S_x covers the universe exactly once iff every clause
index is contained in exactly one chosen S_x, i.e. iff every clause has exactly
one true variable.  So the Exact Cover instance is a yes-instance exactly when
the formula is 1-in-3 satisfiable.

Variables that occur in no clause yield empty sets, which never matter and are
dropped.  Duplicate clauses become distinct universe elements, correctly
requiring each copy to have exactly one true variable.  If there are no clauses
the universe is empty, which is a yes-instance.
"""


def reduce(instance):
    """Return an Exact Cover instance equivalent to the 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # sets[v] = clause indices in which variable (v+1) occurs.
    sets = [[] for _ in range(num_vars)]
    for index, clause in enumerate(clauses):
        for variable in clause:
            sets[variable - 1].append(index)

    # Empty sets never affect an exact cover; drop them.
    sets = [s for s in sets if s]

    return {"universe_size": len(clauses), "sets": sets}
