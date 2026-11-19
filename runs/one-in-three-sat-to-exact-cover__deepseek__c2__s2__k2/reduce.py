"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Source (1-in-3-SAT, positive):
    {"num_vars": m, "clauses": [[a, b, c], ...]}
    Each clause is three distinct positive variables; a clause is satisfied
    when EXACTLY ONE of its three variables is true.

Target (Exact Cover):
    {"universe_size": u, "sets": [[element, ...], ...]}
    Choose pairwise-disjoint sets whose union is the whole universe 0..u-1.

Construction
------------
Create one universe element per clause *occurrence*, so the elements are
0 .. len(clauses)-1 (duplicate clauses therefore get distinct elements).
For every variable v create the set of all clause indices whose clause
contains v.  Selecting the set of v in an exact cover corresponds to
declaring v true.

Correctness
-----------
* Satisfying assignment -> exact cover: let T be the set of true variables.
  Every clause contains exactly one variable of T, so the sets {S_v : v in T}
  are pairwise disjoint (no clause lies in two of them) and their union is
  every clause element.
* Exact cover -> satisfying assignment: an exact cover selects some variable
  sets.  Since each clause element is covered exactly once, each clause
  contains exactly one selected variable.  Declaring selected variables true
  and the rest false makes exactly one variable true per clause.

The reduction builds one element per clause and one set per variable, so it
runs in linear (hence polynomial) time in the input size and does not call
any solver.
"""


def reduce(instance):
    """Reduce a positive 1-in-3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # One universe element per clause occurrence.
    universe_size = len(clauses)

    # sets[v] = indices of the clauses that contain variable v.
    # Slot 0 is unused because variables are numbered 1..num_vars.
    sets = [[] for _ in range(num_vars + 1)]
    for index, clause in enumerate(clauses):
        for variable in clause:
            sets[variable].append(index)

    # Drop the unused slot 0; variables that never occur yield empty sets,
    # which are valid and never affect an exact cover.
    return {"universe_size": universe_size, "sets": sets[1:]}
