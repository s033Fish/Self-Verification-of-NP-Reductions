"""Polynomial-time reduction from 1-in-3-SAT to Exact Cover.

Construction (cycle gadget):

For each variable v that occurs k_v >= 1 times, create a cycle of 2*k_v
elements e_1..e_{2k_v}.  The cycle edges are the sets
    true-edge  t : {e_{2t-1}, e_{2t}}          (t = 1..k_v)
    false-edge t : {e_{2t},   e_{2t+1}}        (indices mod 2k_v)
A cycle of even length has exactly two perfect matchings, the "true"
matching (all true-edges) and the "false" matching (all false-edges).

For each clause C_j = (a, b, c) create a fresh clause element d_j and the
three sets
    {d_j} u true-edge(a)  u false-edge(b) u false-edge(c)   # a is the true one
    {d_j} u false-edge(a) u true-edge(b)  u false-edge(c)   # b is the true one
    {d_j} u false-edge(a) u false-edge(b) u true-edge(c)    # c is the true one
using the occurrence of each variable in this clause.

Choosing one of these covers d_j and removes one edge from each of the
three gadgets.  The remaining elements of a gadget admit a perfect
matching iff the removed edges are all true-edges or all false-edges,
i.e. iff every clause containing that variable agrees on its truth value.
Hence exact covers correspond exactly to assignments in which every clause
has exactly one true variable.
"""

from __future__ import annotations


def reduce(instance):
    """Return an Exact Cover instance equivalent to the 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # occurrences[v] = clause indices containing variable v, in order.
    occurrences = {v: [] for v in range(1, num_vars + 1)}
    for j, clause in enumerate(clauses):
        for v in clause:
            occurrences[v].append(j)

    # Base element index of each variable's cycle gadget.
    base = {}
    counter = 0
    for v in range(1, num_vars + 1):
        base[v] = counter
        counter += 2 * len(occurrences[v])

    # Occurrence number of variable v inside clause j.
    occ_num = {}
    for v in range(1, num_vars + 1):
        for t, j in enumerate(occurrences[v]):
            occ_num[(v, j)] = t

    def true_edge(v, t):
        b = base[v]
        return [b + 2 * t, b + 2 * t + 1]

    def false_edge(v, t):
        b = base[v]
        k = len(occurrences[v])
        return [b + 2 * t + 1, b + ((2 * t + 2) % (2 * k))]

    sets = []

    # Cycle edges for every variable gadget.
    for v in range(1, num_vars + 1):
        for t in range(len(occurrences[v])):
            sets.append(true_edge(v, t))
            sets.append(false_edge(v, t))

    # Clause elements and clause sets.
    for j, clause in enumerate(clauses):
        d = counter
        counter += 1
        a, b, c = clause
        ta = occ_num[(a, j)]
        tb = occ_num[(b, j)]
        tc = occ_num[(c, j)]
        sets.append([d] + true_edge(a, ta) + false_edge(b, tb) + false_edge(c, tc))
        sets.append([d] + false_edge(a, ta) + true_edge(b, tb) + false_edge(c, tc))
        sets.append([d] + false_edge(a, ta) + false_edge(b, tb) + true_edge(c, tc))

    return {"universe_size": counter, "sets": sets}
