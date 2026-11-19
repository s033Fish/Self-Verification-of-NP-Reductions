"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Idea
----
Given a positive 1-in-3-SAT instance with m variables and clauses
c_0, ..., c_{n-1}, build an Exact Cover instance whose universe is the set
of clause indices {0, ..., n-1}.

For each variable v (1..m) create one set S_v consisting of the indices of
all clauses that contain v.  A variable that occurs in no clause yields the
empty set, which never matters for Exact Cover.

Choosing a set S_v corresponds to setting variable v to true.  A collection
of chosen sets is an exact cover of the universe iff:

  * the chosen sets are pairwise disjoint, i.e. no clause index is contained
    in two chosen sets, i.e. no clause has two true variables; and
  * their union is the whole universe, i.e. every clause has at least one
    true variable.

Together these say every clause has EXACTLY ONE true variable, which is
precisely the 1-in-3-SAT condition.  Conversely any satisfying assignment
yields the exact cover formed by the sets of the true variables.

The construction is linear in the size of the input, hence polynomial time.
"""


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to an Exact Cover instance.

    instance: {"num_vars": m, "clauses": [[a, b, c], ...]}
    returns:  {"universe_size": n, "sets": [[...], ...]}
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One universe element per clause (identified by its index).
    universe_size = len(clauses)

    # For each variable, collect the indices of the clauses containing it.
    variable_sets = [[] for _ in range(num_vars + 1)]
    for index, clause in enumerate(clauses):
        for variable in clause:
            variable_sets[variable].append(index)

    # One set per variable; variables 1..m map to sets[0..m-1].
    sets = [variable_sets[v] for v in range(1, num_vars + 1)]

    return {"universe_size": universe_size, "sets": sets}
