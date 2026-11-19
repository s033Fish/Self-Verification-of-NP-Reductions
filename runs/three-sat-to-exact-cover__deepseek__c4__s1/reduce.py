"""Polynomial-time reduction from 3-SAT (ThreeSat) to Exact Cover.

Construction
------------
Let the formula have variables 1..m and clauses C_0..C_{k-1}.

Universe elements
  * g_x                     : one "garbage" element per variable x (1..m)
  * c_j                     : one element per clause C_j
  * e_{j,p}                 : one element per literal occurrence (clause j, position p)

Sets
  * PosGarbage_x = {g_x} U { e_{j,p} : the occurrence at (j,p) is the literal +x }
  * NegGarbage_x = {g_x} U { e_{j,p} : the occurrence at (j,p) is the literal -x }
  * { e_{j,p} }             : singleton for every occurrence
  * { e_{j,p}, c_j }        : clause set for every occurrence

Why it works
------------
g_x must be covered exactly once, by PosGarbage_x or NegGarbage_x.
  * If PosGarbage_x is chosen it covers every positive copy of x, so no clause
    set using +x can be chosen: x is used as a witness only negatively (or not
    at all).
  * If NegGarbage_x is chosen, symmetrically no clause set using -x is chosen.
Hence a valid exact cover can never select a +x occurrence and a -x occurrence
of the same variable.  Each clause element c_j is contained only in the clause
sets of C_j, so exactly one literal occurrence of each clause is selected.

Conversely, a satisfying assignment yields an exact cover: for each clause pick
one true literal's occurrence (clause set), for each variable choose the garbage
set that forbids the side not used (if a positive occurrence is selected choose
NegGarbage_x, else PosGarbage_x), and cover every unselected occurrence with its
singleton.  This covers everything exactly once.
"""

from __future__ import annotations


def reduce(instance):
    """Return an Exact Cover instance equivalent to the given 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    k = len(clauses)

    # Element indices.
    #   g_x      -> x - 1                     (0 .. num_vars-1)
    #   c_j      -> num_vars + j              (num_vars .. num_vars+k-1)
    #   e_{j,p}  -> num_vars + k + occ_index  (occurrences in clause order)
    clause_base = num_vars
    occ_base = num_vars + k

    # Collect occurrence element indices per variable and per sign.
    pos_copies = {x: [] for x in range(1, num_vars + 1)}
    neg_copies = {x: [] for x in range(1, num_vars + 1)}

    sets = []

    occ_index = 0
    for j, clause in enumerate(clauses):
        c_elem = clause_base + j
        for literal in clause:
            e = occ_base + occ_index
            occ_index += 1
            var = abs(literal)
            if literal > 0:
                pos_copies[var].append(e)
            else:
                neg_copies[var].append(e)
            # singleton and clause set for this occurrence
            sets.append([e])
            sets.append([e, c_elem])

    # Garbage sets per variable.
    for x in range(1, num_vars + 1):
        g = x - 1
        sets.append([g] + pos_copies[x])
        sets.append([g] + neg_copies[x])

    universe_size = num_vars + k + occ_index
    return {"universe_size": universe_size, "sets": sets}
