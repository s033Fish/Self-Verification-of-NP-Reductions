"""Polynomial-time reduction from SAT to 3-SAT.

Reduction outline
-----------------
Given a CNF formula over variables 1..m, we build an equisatisfiable 3-CNF
formula over variables 1..m plus some fresh auxiliary variables.

For each source clause we first normalise it:
  * duplicate literals are removed;
  * a clause containing both v and -v is a tautology and is dropped.

Then, with k the number of distinct literals left:
  * k == 0 : the clause is unsatisfiable.  Emit an unsatisfiable gadget
             (all 8 clauses over 3 fresh variables).
  * k == 1 : force the single literal to be true with 4 clauses.
  * k == 2 : force "l1 or l2" with 2 clauses using one fresh variable.
  * k == 3 : emit the clause unchanged.
  * k >= 4: split with the standard chain of fresh variables z_1..z_{k-3}:
             (l1 v l2 v z1),
             (~z1 v l3 v z2), ...,
             (~z_{k-4} v l_{k-1} v z_{k-3}),
             (~z_{k-3} v l_{k-1} v l_k)
            (the last two shown for clarity; indices follow the code).

All introduced clauses have exactly 3 literals on 3 distinct variables, so
the result is a valid 3-SAT instance.  The construction is linear in the
size of the input.
"""

from __future__ import annotations


def reduce(instance):
    """Return a 3-SAT instance equisatisfiable with the given SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = num_vars
    out_clauses = []

    def fresh():
        nonlocal next_var
        next_var += 1
        return next_var

    def add_unsat_gadget():
        # All 8 clauses over 3 fresh variables: unsatisfiable.
        p, q, r = fresh(), fresh(), fresh()
        for a in (p, -p):
            for b in (q, -q):
                for c in (r, -r):
                    out_clauses.append([a, b, c])

    for clause in clauses:
        # Normalise: drop duplicate literals; detect tautologies.
        lits = []
        seen = set()
        tautology = False
        for literal in clause:
            if -literal in seen:
                tautology = True
                break
            if literal not in seen:
                seen.add(literal)
                lits.append(literal)
        if tautology:
            continue

        k = len(lits)
        if k == 0:
            add_unsat_gadget()
        elif k == 1:
            (l,) = lits
            a, b = fresh(), fresh()
            out_clauses.append([l, a, b])
            out_clauses.append([l, -a, b])
            out_clauses.append([l, a, -b])
            out_clauses.append([l, -a, -b])
        elif k == 2:
            l1, l2 = lits
            a = fresh()
            out_clauses.append([l1, l2, a])
            out_clauses.append([l1, l2, -a])
        elif k == 3:
            out_clauses.append(list(lits))
        else:
            zs = [fresh() for _ in range(k - 3)]
            out_clauses.append([lits[0], lits[1], zs[0]])
            for i in range(1, k - 3):
                out_clauses.append([-zs[i - 1], lits[i + 1], zs[i]])
            out_clauses.append([-zs[k - 4], lits[k - 2], lits[k - 1]])

    return {"num_vars": next_var, "clauses": out_clauses}
