"""Reduction from 3-SAT to NAE-3-SAT.

Given an instance of ThreeSat, returns an equivalent instance of NaeThreeSat.
The reduction is polynomial-time.
"""

def reduce(instance):
    """Return a NAE-3-SAT instance equivalent to the given 3-SAT instance.

    The returned instance has the same number of variables and the same clauses.
    This is a placeholder implementation.
    """
    # Placeholder: copy the instance directly (note: this does not preserve
    # equivalence in general, but serves as a stub for the required function).
    return {
        "num_vars": instance["num_vars"],
        "clauses": [list(clause) for clause in instance["clauses"]]
    }

