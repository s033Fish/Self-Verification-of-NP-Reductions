"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

SOURCE (OneInThreeSat): {"num_vars": m, "clauses": [[a, b, c], ...]}
TARGET (ExactCover):    {"universe_size": u, "sets": [[element, ...], ...]}

Reduction idea
--------------
Make the universe the set of clauses (clause i becomes element i).  For each
variable v, create the set S_v = { i : v occurs in clauses[i] }.  Choosing a
collection of sets in the Exact Cover instance is then the same as choosing a
collection of variables to be TRUE:

  * pairwise disjointness  <=> no clause contains two chosen variables;
  * union = whole universe  <=> every clause contains at least one chosen
                               variable.

Together these say every clause contains *exactly one* chosen (TRUE) variable,
which is precisely the 1-in-3-SAT yes-condition.  Variables that occur in no
clause simply produce empty sets, which never matter.  A formula with no
clauses gives universe_size = 0, which Exact Cover accepts by choosing nothing.

The construction takes O(num_vars + total literals) time, hence polynomial.
"""


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to an Exact Cover instance.

    Returns {"universe_size": number_of_clauses,
             "sets": [clause indices containing variable v, for v = 1..m]}
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # sets[v - 1] will collect the indices of clauses containing variable v.
    sets = [[] for _ in range(num_vars)]

    for index, clause in enumerate(clauses):
        for var in clause:
            # Variables are guaranteed to be in 1..num_vars by the source
            # problem's validation.
            sets[var - 1].append(index)

    return {"universe_size": len(clauses), "sets": sets}
