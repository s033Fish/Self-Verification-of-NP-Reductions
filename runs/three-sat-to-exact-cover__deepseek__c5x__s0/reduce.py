"""Polynomial-time reduction from 3-SAT to Exact Cover.

Construction
------------
For a 3-SAT instance with m variables and n clauses, build a universe with:

  * one selector element d_i per variable i (1..m);
  * one occurrence element o_{j,k} for each clause j and position k in 0..2;
  * one clause element c_j per clause j;
  * one private element p_{j,k} per clause j and position k.

Sets:

  * variable gadget, for each variable i:
        POS_i = {d_i} U {o_{j,k} : literal at (j,k) is +i}
        NEG_i = {d_i} U {o_{j,k} : literal at (j,k) is -i}
    Both contain d_i, so exactly one is chosen.  Choosing POS_i means x_i is
    false (it covers the occurrences of the positive literal), choosing NEG_i
    means x_i is true (it covers the occurrences of the negative literal).
    The occurrences of the *true* literal of x_i are therefore left free for
    clause gadgets.

  * clause gadget, for each clause j and position k:
        L_{j,k} = {c_j, o_{j,k}}
        P_{j,k} = {o_{j,k}, p_{j,k}}
        D_{j,k} = {p_{j,k}}

    c_j can only be covered by an L set, so exactly one L_{j,k} is chosen;
    this requires o_{j,k} to be free, i.e. the literal at (j,k) to be true.
    Hence every clause needs a true literal.  Any other free occurrence
    element of the clause is covered by its P set, and an occurrence element
    already covered by the variable gadget has its private element covered by
    the D singleton.  Thus a cover exists exactly when the formula is
    satisfiable.
"""

from __future__ import annotations


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    nc = len(clauses)

    nxt = 0
    d_var = []
    for _ in range(m):
        d_var.append(nxt)
        nxt += 1

    occ = [[0, 0, 0] for _ in range(nc)]
    for j in range(nc):
        for k in range(3):
            occ[j][k] = nxt
            nxt += 1

    cl = []
    for _ in range(nc):
        cl.append(nxt)
        nxt += 1

    priv = [[0, 0, 0] for _ in range(nc)]
    for j in range(nc):
        for k in range(3):
            priv[j][k] = nxt
            nxt += 1

    universe_size = nxt
    sets = []

    # Variable gadgets.
    for i in range(m):
        pos = [d_var[i]]  # covers occurrences of +i  (chosen when x_i false)
        neg = [d_var[i]]  # covers occurrences of -i  (chosen when x_i true)
        for j in range(nc):
            for k in range(3):
                lit = clauses[j][k]
                if lit == i + 1:
                    pos.append(occ[j][k])
                elif lit == -(i + 1):
                    neg.append(occ[j][k])
        sets.append(pos)
        sets.append(neg)

    # Clause gadgets.
    for j in range(nc):
        for k in range(3):
            sets.append([cl[j], occ[j][k]])
            sets.append([occ[j][k], priv[j][k]])
            sets.append([priv[j][k]])

    return {"universe_size": universe_size, "sets": sets}
