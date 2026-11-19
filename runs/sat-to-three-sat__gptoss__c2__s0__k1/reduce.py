"""Reduction from SAT to 3‑SAT.

The source problem (Sat) allows clauses of any length (including the empty
clause) and may contain duplicate literals or both a literal and its
negation.  The target problem (ThreeSat) requires every clause to contain
exactly three *different* variables, none of which appear both positively and
negatively in the same clause.

This file implements a classic polynomial‑time reduction that converts an
arbitrary SAT instance into an equivalent 3‑SAT instance.  The construction
follows the textbook transformation:

* Remove duplicate literals from each clause.
* If a clause contains a variable together with its negation it is a
  tautology and can be omitted.
* For a clause of size 1 we introduce two fresh variables and add the four
  clauses that force the original literal to be true.
* For a clause of size 2 we introduce one fresh variable and replace the
  clause with two 3‑clauses that together are equivalent to the original.
* For a clause of size ≥ 3 we break it into a chain of 3‑clauses using fresh
  auxiliary variables.
* An empty clause makes the whole formula unsatisfiable; we return a fixed
  unsatisfiable 3‑SAT instance ( (x ∨ y ∨ z) ∧ (¬x ∨ ¬y ∨ ¬z) ).

The function runs in time linear in the size of the input plus the number of
auxiliary variables introduced, which is polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _is_tautology(lits: List[int]) -> bool:
    """Return ``True`` if the clause contains a variable together with its
    negation.
    """
    seen = set()
    for lit in lits:
        if -lit in seen:
            return True
        seen.add(lit)
    return False


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        Dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        lists of literals).  The format matches the ``Sat`` class description.

    Returns
    -------
    dict
        A 3‑SAT instance in the format required by the ``ThreeSat`` class.
    """

    m: int = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    # If there is an empty clause the formula is unsatisfiable.  Return a
    # simple unsatisfiable 3‑SAT instance.
    for cl in original_clauses:
        if len(cl) == 0:
            unsat_vars = max(m, 3)
            return {
                "num_vars": unsat_vars,
                "clauses": [[1, 2, 3], [-1, -2, -3]],
            }

    # If there are no clauses at all, the formula is trivially satisfiable.
    if not original_clauses:
        return {"num_vars": m, "clauses": []}

    new_clauses: List[List[int]] = []
    next_var = m + 1  # next fresh variable index

    for clause in original_clauses:
        # Remove duplicate literals while preserving order.
        uniq = list(dict.fromkeys(clause))
        # Skip tautological clauses – they are always satisfied.
        if _is_tautology(uniq):
            continue
        k = len(uniq)
        if k == 0:
            continue  # already handled empty clause case
        if k == 1:
            l = uniq[0]
            a = next_var
            b = next_var + 1
            next_var += 2
            # Four clauses forcing l to be true.
            new_clauses.append([l, a, b])
            new_clauses.append([l, a, -b])
            new_clauses.append([l, -a, b])
            new_clauses.append([l, -a, -b])
        elif k == 2:
            l1, l2 = uniq
            y = next_var
            next_var += 1
            new_clauses.append([l1, l2, y])
            new_clauses.append([l1, l2, -y])
        else:  # k >= 3
            lits = uniq
            if k == 3:
                new_clauses.append(lits)
            else:
                # Introduce auxiliary variables y1 .. y_{k-3}
                aux_vars = []
                for _ in range(k - 3):
                    aux_vars.append(next_var)
                    next_var += 1
                # First clause: (l1 ∨ l2 ∨ y1)
                new_clauses.append([lits[0], lits[1], aux_vars[0]])
                # Middle clauses
                for i in range(2, k - 2):
                    new_clauses.append([
                        -aux_vars[i - 2],
                        lits[i],
                        aux_vars[i - 1],
                    ])
                # Last clause: (¬y_{k-3} ∨ l_{k-1} ∨ l_k)
                new_clauses.append([
                    -aux_vars[-1],
                    lits[-2],
                    lits[-1],
                ])

    final_num_vars = max(m, next_var - 1)
    return {"num_vars": final_num_vars, "clauses": new_clauses}

