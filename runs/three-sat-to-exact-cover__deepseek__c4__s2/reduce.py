"""Polynomial-time reduction from 3-SAT (ThreeSat) to Exact Cover (ExactCover).

Construction
------------
Elements:
  * one element v_i per variable i (1..m),
  * one auxiliary element e_{j,k} for each literal occurrence k of clause j,
  * one element c_j per clause j.

Sets:
  * For each variable i, two sets
        T_i = {v_i} union {e_{j,k} : clause j has literal  x_i at position k}
        F_i = {v_i} union {e_{j,k} : clause j has literal -x_i at position k}
    Exactly one of them is picked, fixing the truth value of x_i.
  * For each clause j with occurrences e_{j,1},e_{j,2},e_{j,3} and element c_j,
    the seven gadget sets
        {c_j}, {c_j,e1}, {c_j,e2}, {c_j,e3},
        {c_j,e1,e2}, {c_j,e1,e3}, {c_j,e2,e3}.
    The gadget can cover c_j together with the auxiliaries of any subset of
    at most two literals, but NOT all three.  A gadget set may only use
    auxiliaries that the variable sets did not already cover, i.e. literals
    that are false.  Hence an exact cover exists iff every clause has at
    least one true literal.

The construction is linear in the size of the input.
"""

from __future__ import annotations


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    nxt = 0
    var_elem = list(range(nxt, nxt + m))
    nxt += m

    # aux[j][k] : auxiliary element of the k-th literal of clause j
    aux = []
    for _ in range(n):
        row = list(range(nxt, nxt + 3))
        nxt += 3
        aux.append(row)

    clause_elem = list(range(nxt, nxt + n))
    nxt += n
    universe_size = nxt

    sets = []

    # Variable sets.
    for i in range(m):
        var = i + 1
        pos = [aux[j][k] for j in range(n) for k in range(3) if clauses[j][k] == var]
        neg = [aux[j][k] for j in range(n) for k in range(3) if clauses[j][k] == -var]
        sets.append([var_elem[i]] + pos)
        sets.append([var_elem[i]] + neg)

    # Clause gadgets.
    for j in range(n):
        c = clause_elem[j]
        e = aux[j]
        sets.append([c])
        for k in range(3):
            sets.append([c, e[k]])
        for k in range(3):
            for l in range(k + 1, 3):
                sets.append([c, e[k], e[l]])

    return {"universe_size": universe_size, "sets": sets}
