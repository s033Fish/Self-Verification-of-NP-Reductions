"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

Input:  {"num_vars": m, "clauses": [[literal, ...], ...]}   (Sat)
Output: {"num_vars": M, "clauses": [[l1, l2, l3], ...]}     (ThreeSat)

Every output clause has exactly three literals on three distinct
variables, and the output is satisfiable iff the input is.

Method
------
First each input clause is normalised:
  * a clause containing both v and -v is a tautology and is dropped;
  * repeated literals are removed.
Then a clause with k distinct literals is encoded:
  * k == 0: eight clauses over three fresh variables (all sign patterns),
    which is unsatisfiable;
  * k == 1: [l, a, b], [l, a, -b], [l, -a, b], [l, -a, -b] with fresh a,b;
  * k == 2: [l1, l2, a], [l1, l2, -a] with fresh a;
  * k == 3: kept as is;
  * k >= 4: the standard chain introducing fresh y1..y_{k-3}:
        [l1, l2, y1],
        [-y1, l3, y2], ..., [-y_{k-4}, l_{k-2}, y_{k-3}],
        [-y_{k-3}, l_{k-1}, l_k].
All fresh variables are distinct and larger than every input variable, so
no output clause repeats a variable or contains a complementary pair.
The number of fresh variables is O(total input literals), hence the
reduction runs in polynomial time.
"""

from __future__ import annotations


def reduce(instance):
    """Return a 3-SAT instance equisatisfiable with the given SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = num_vars + 1
    output_clauses = []

    def fresh():
        nonlocal next_var
        var = next_var
        next_var += 1
        return var

    for clause in clauses:
        # Remove duplicate literals; detect tautologies (v and -v together).
        seen = set()
        literals = []
        tautology = False
        for literal in clause:
            if -literal in seen:
                tautology = True
                break
            if literal not in seen:
                seen.add(literal)
                literals.append(literal)
        if tautology:
            continue

        k = len(literals)

        if k == 0:
            # Empty clause: encode as an unsatisfiable 3-CNF over fresh vars.
            a, b, c = fresh(), fresh(), fresh()
            for sa in (1, -1):
                for sb in (1, -1):
                    for sc in (1, -1):
                        output_clauses.append([sa * a, sb * b, sc * c])

        elif k == 1:
            (lit,) = literals
            a, b = fresh(), fresh()
            output_clauses.append([lit, a, b])
            output_clauses.append([lit, a, -b])
            output_clauses.append([lit, -a, b])
            output_clauses.append([lit, -a, -b])

        elif k == 2:
            l1, l2 = literals
            a = fresh()
            output_clauses.append([l1, l2, a])
            output_clauses.append([l1, l2, -a])

        elif k == 3:
            output_clauses.append(list(literals))

        else:
            # k >= 4: chain of 3-clauses with k - 3 fresh variables.
            ys = [fresh() for _ in range(k - 3)]
            output_clauses.append([literals[0], literals[1], ys[0]])
            for j in range(1, k - 3):
                output_clauses.append([-ys[j - 1], literals[j + 1], ys[j]])
            output_clauses.append([-ys[-1], literals[k - 2], literals[k - 1]])

    return {"num_vars": next_var - 1, "clauses": output_clauses}
