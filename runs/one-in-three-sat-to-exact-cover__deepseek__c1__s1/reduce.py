"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Construction
------------
A positive 1-in-3-SAT instance asks for a truth assignment in which every
clause has *exactly one* true variable.

Build one universe element per clause, and for every variable v one set S_v
containing the elements of all clauses in which v occurs.

An exact cover of this set system is a sub-collection of the S_v that is
pairwise disjoint and whose union is every clause element:

  * pairwise disjoint  <=> no clause contains two chosen variables
                           (so at most one chosen variable per clause);
  * union is everything <=> every clause contains a chosen variable
                           (so at least one chosen variable per clause).

Together these say that every clause contains exactly one chosen variable.
Declaring variable v true exactly when S_v is chosen therefore gives a
satisfying assignment, and conversely any satisfying assignment yields such
an exact cover by choosing the sets of the true variables.

Variables occurring in no clause produce empty sets, which never affect an
exact cover; this matches the fact that their truth value is unconstrained.

Duplicate clauses get distinct universe elements, which is harmless because
they impose the same "exactly one true" constraint.

The construction is linear in the size of the formula, hence polynomial.
"""


def reduce(instance):
    """Map a 1-in-3-SAT instance to an equisatisfiable Exact Cover instance.

    Source format:  {"num_vars": m, "clauses": [[a, b, c], ...]}
    Target format:  {"universe_size": u, "sets": [[element, ...], ...]}
    """
    clauses = instance["clauses"]
    num_vars = instance["num_vars"]

    # One universe element per clause.  Element c corresponds to clauses[c].
    universe_size = len(clauses)

    # S_v = elements of the clauses that contain variable v.
    sets = [
        [c for c, clause in enumerate(clauses) if v in clause]
        for v in range(1, num_vars + 1)
    ]

    return {"universe_size": universe_size, "sets": sets}
