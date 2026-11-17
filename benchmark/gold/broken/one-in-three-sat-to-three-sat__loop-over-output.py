"""Broken: loops over the clause list while appending to it.

Each pass adds 6 clauses, so the loop never reaches the end.
Expect timeout on the first instance with a clause.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = list(instance["clauses"])
    z = num_vars + 1
    for a, b, c in clauses:  # should loop over instance["clauses"]
        for p, q in ((a, b), (a, c), (b, c)):
            clauses.append([-p, -q, z])
            clauses.append([-p, -q, -z])
    return {"num_vars": num_vars + 1, "clauses": clauses}