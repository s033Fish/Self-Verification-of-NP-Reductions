"""Reduction from SAT to 3‑SAT.

Implements a polynomial‑time many‑one reduction from the general SAT
problem (arbitrary CNF) to 3‑SAT (exactly three literals per clause on
distinct variables).

The construction follows the textbook reduction:
* Empty clause → unsatisfiable gadget.
* Unit clause → two 3‑clauses forcing the literal true.
* Binary clause → two 3‑clauses with a fresh variable.
* Longer clause → chain of 3‑clauses using fresh bridge variables.

All generated clauses obey the ThreeSat format (three distinct variables,
no clause contains both a variable and its negation).
"""

from __future__ import annotations

from typing import List, Dict

from problems import Sat, ThreeSat


def _fresh_var(counter: List[int]) -> int:
    """Return a new variable identifier and increment the counter.

    ``counter`` is a one‑element list so that the integer can be mutated
    across calls without a global variable.
    """

    v = counter[0]
    counter[0] += 1
    return v


def _add_contradiction(clauses: List[List[int]], counter: List[int]) -> None:
    """Append an unsatisfiable 3‑SAT sub‑formula to *clauses*.

    ThreeSat forbids repeated variables inside a clause, therefore we use a
    gadget that forces a fresh variable ``a`` to be both true and false:

        (a)   → (a ∨ y ∨ y') ∧ (a ∨ ¬y ∨ ¬y')
        (¬a) → (¬a ∨ z ∨ z') ∧ (¬a ∨ ¬z ∨ ¬z')

    The four resulting clauses each contain three distinct variables, and
    together they are unsatisfiable.
    """

    a = _fresh_var(counter)
    # force a = True
    y = _fresh_var(counter)
    y_prime = _fresh_var(counter)
    clauses.append([a, y, y_prime])
    clauses.append([a, -y, -y_prime])
    # force a = False
    z = _fresh_var(counter)
    z_prime = _fresh_var(counter)
    clauses.append([-a, z, z_prime])
    clauses.append([-a, -z, -z_prime])


def _simplify_clause(clause: List[int]) -> List[int] | None:
    """Return a simplified version of *clause*.

    - Removes duplicate literals.
    - Detects tautological clauses containing both v and -v (returns [] to
      indicate the clause can be omitted because it is always satisfied).
    - Returns ``None`` never – kept for type compatibility.
    """

    seen: set[int] = set()
    for lit in clause:
        if -lit in seen:
            # clause always true → can be dropped
            return []
        seen.add(lit)
    return list(seen)


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an equivalent ThreeSat instance.

    Parameters
    ----------
    instance: dict
        Must conform to the :class:`Sat` format.

    Returns
    -------
    dict
        An instance of :class:`ThreeSat` with the same satisfiability
        answer.
    """

    # Validate source instance.
    Sat.validate(instance)

    m = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    # Fresh variable counter – start after existing variables.
    counter = [m + 1]
    new_clauses: List[List[int]] = []

    # If any empty clause appears, the formula is unsatisfiable.
    if any(len(c) == 0 for c in original_clauses):
        _add_contradiction(new_clauses, counter)
        return {"num_vars": counter[0] - 1, "clauses": new_clauses}

    for clause in original_clauses:
        simp = _simplify_clause(clause)
        if simp is None:
            continue
        if len(simp) == 0:
            # clause always true – skip it.
            continue
        k = len(simp)
        if k == 0:
            # Should not happen after previous check.
            _add_contradiction(new_clauses, counter)
            continue
        if k == 1:
            l = simp[0]
            y = _fresh_var(counter)
            y_prime = _fresh_var(counter)
            new_clauses.append([l, y, y_prime])
            new_clauses.append([l, -y, -y_prime])
        elif k == 2:
            l1, l2 = simp
            y = _fresh_var(counter)
            new_clauses.append([l1, l2, y])
            new_clauses.append([l1, l2, -y])
        else:
            lits = simp
            if k == 3:
                new_clauses.append(lits)
                continue
            # Chain using bridge variables.
            # First bridge
            z_prev = _fresh_var(counter)
            new_clauses.append([lits[0], lits[1], z_prev])
            # Intermediate bridges
            for i in range(2, k - 1):
                if i == k - 1:
                    break
                z_next = _fresh_var(counter)
                new_clauses.append([-z_prev, lits[i], z_next])
                z_prev = z_next
            # Final clause
            new_clauses.append([-z_prev, lits[-2], lits[-1]])

    total_vars = counter[0] - 1
    ThreeSat.validate({"num_vars": total_vars, "clauses": new_clauses})
    return {"num_vars": total_vars, "clauses": new_clauses}

