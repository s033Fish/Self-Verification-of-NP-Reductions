"""Polynomial-time reduction from 1-in-3-SAT to 3-SAT.

For each source clause (a, b, c), where exactly one of a, b, c must be true,
we emit the following five 3-SAT clauses:

    ( a  v  b  v  c)
    (~a  v ~b  v ~c)
    (~a  v ~b  v  c)
    (~a  v  b  v ~c)
    ( a  v ~b  v ~c)

These clauses are all falsified by exactly the five assignments in which the
number of true variables among a, b, c is not one:
    000, 011, 101, 110, 111.
The three assignments with exactly one true variable satisfy all five clauses.
Thus the whole 3-CNF is satisfiable iff the original 1-in-3-SAT instance is.
No auxiliary variables are needed.
"""


def reduce(instance):
    """Return a 3-SAT instance equivalent to the given 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    target_clauses = []

    for a, b, c in instance["clauses"]:
        target_clauses.append([a, b, c])
        target_clauses.append([-a, -b, -c])
        target_clauses.append([-a, -b, c])
        target_clauses.append([-a, b, -c])
        target_clauses.append([a, -b, -c])

    return {"num_vars": num_vars, "clauses": target_clauses}
