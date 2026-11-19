"""Polynomial-time reduction from positive 1-in-3-SAT to Exact Cover.

Source instance
---------------
    {"num_vars": m, "clauses": [[a, b, c], ...]}

Target instance
---------------
    {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
For every clause j we create one element d_j.  For every *occurrence* of a
variable x (i.e. every position where x appears in some clause) we create two
elements p and n, meaning "x is true at this occurrence" and "x is false at
this occurrence".

For a clause (a, b, c) we add three sets, one for each possible choice of the
unique true variable.  The set for choosing a is

    {d_j, p(a), n(b), n(c)}

and similarly for b and c.  Since d_j occurs in no other set, an exact cover
must choose exactly one of these three sets, i.e. exactly one variable of the
clause is marked true.

To make the choices consistent across all occurrences of the same variable x,
let its occurrences be 1..k.  We add the two auxiliary sets

    {n_1, ..., n_k}      (chosen when x is true everywhere)
    {p_1, ..., p_k}      (chosen when x is false everywhere)

If the clause sets ever marked x true in one occurrence and false in another,
then some n_i and some p_j would both be uncovered.  The only set containing
n_i is the first auxiliary set, but it also contains an already covered n, and
likewise for p_j; hence no exact cover exists for a mixed choice.  Conversely,
any global assignment gives an exact cover: pick the set of the true variable
in each clause, then pick the auxiliary set that covers the remaining elements
of each variable.

This is clearly polynomial in the size of the input.
"""


def reduce(instance):
    """Reduce a 1-in-3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Element ids are allocated as we go.
    next_id = 0

    # One element per clause.
    clause_element = []
    for _ in clauses:
        clause_element.append(next_id)
        next_id += 1

    # For each variable, the (p, n) element pairs of its occurrences, in the
    # order the occurrences appear.  For each clause we also remember the
    # (p, n) pairs of its three positions.
    occurrence_pairs = {v: [] for v in range(1, num_vars + 1)}
    clause_pairs = []
    for clause in clauses:
        pairs = []
        for v in clause:
            p = next_id
            n = next_id + 1
            next_id += 2
            occurrence_pairs[v].append((p, n))
            pairs.append((p, n))
        clause_pairs.append(pairs)

    universe_size = next_id
    sets = []

    # Clause gadgets: exactly one of the three variables is true.
    for j, pairs in enumerate(clause_pairs):
        d = clause_element[j]
        for chosen in range(3):
            subset = [d]
            for i in range(3):
                p, n = pairs[i]
                subset.append(p if i == chosen else n)
            sets.append(subset)

    # Consistency gadgets: all occurrences of a variable get the same value.
    for v in range(1, num_vars + 1):
        pairs = occurrence_pairs[v]
        if pairs:
            sets.append([n for (_p, n) in pairs])
            sets.append([p for (p, _n) in pairs])

    return {"universe_size": universe_size, "sets": sets}
