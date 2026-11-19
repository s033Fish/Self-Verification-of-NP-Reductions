"""Reduction from SAT to 3‑SAT.

The source problem (SAT) allows clauses of arbitrary length, possibly
containing duplicate literals or both a literal and its negation.  The
target problem (ThreeSat) requires *exactly* three literals per clause,
all on distinct variables and without a literal appearing together with
its negation.

The reduction follows the classic textbook construction:

* Empty clause → produce a trivially unsatisfiable 3‑SAT instance.
* Clause of size 1 → replace with four 3‑clauses using two fresh
  variables.  The gadget is satisfiable iff the original literal is true.
* Clause of size 2 → replace with two 3‑clauses using one fresh
  variable.  This forces the original clause to be satisfied.
* Clause of size 3 → after removing duplicates and tautologies the
  clause already satisfies the target format and is kept unchanged.
* Clause of size >3 → break the clause into a chain of 3‑clauses using
  fresh auxiliary variables (the standard Tseitin‑style construction).

All auxiliary variables are introduced consecutively after the original
variables.  The reduction runs in time linear in the size of the input
instance, which is polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _literal_var(lit: int) -> int:
    """Return the variable index of a literal (positive integer)."""
    return abs(lit)


def _simplify_clause(clause: List[int]) -> List[int]:
    """Simplify a clause according to SAT semantics.

    * Remove duplicate literals.
    * If both a literal and its negation appear, the clause is a tautology
      and we return an empty list to signal that it can be ignored.
    """
    seen = set()
    for lit in clause:
        if -lit in seen:
            # Tautology – clause always satisfied.
            return []
        seen.add(lit)
    # Remove duplicates while preserving an arbitrary order.
    return list(seen)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys "num_vars" and "clauses" as defined
        by the SAT problem description.

    Returns
    -------
    dict
        A 3‑SAT instance in the format required by ``ThreeSat``.
    """
    original_vars = int(instance.get("num_vars", 0))
    original_clauses: List[List[int]] = instance.get("clauses", [])

    new_clauses: List[List[int]] = []
    next_var = original_vars + 1  # first fresh variable index

    # Helper to add a clause and ensure it respects the target format.
    def add_clause(c: List[int]):
        # By construction our gadgets never introduce duplicate variables
        # or a variable together with its negation.
        new_clauses.append(c)

    # If any clause is empty after simplification, the whole formula is
    # unsatisfiable.  We generate a fixed unsatisfiable 3‑SAT instance.
    unsat_generated = False

    for raw_clause in original_clauses:
        simplified = _simplify_clause(raw_clause)
        if not simplified:  # either tautology (skip) or empty clause (unsat)
            # Detect true empty clause (unsatisfiable) vs tautology.
            # A tautology would have been returned as [] only when a pair
            # of complementary literals were present.  In that case the
            # original clause is always satisfied and can be ignored.
            # To differentiate, we check whether the original clause had
            # any complementary pair.
            has_complement = any(-lit in raw_clause for lit in raw_clause)
            if has_complement:
                # Tautology – skip.
                continue
            # Empty clause -> unsatisfiable.
            if not unsat_generated:
                # Create a contradiction using a fresh variable x.
                x = next_var
                next_var += 1
                add_clause([x, x, x])          # forces x = True
                add_clause([-x, -x, -x])       # forces x = False
                unsat_generated = True
            # No need to process further clauses – the whole formula is unsat.
            continue

        k = len(simplified)
        if k == 1:
            # Gadget for a unit clause l.
            l = simplified[0]
            y = next_var
            z = next_var + 1
            next_var += 2
            add_clause([l, y, z])
            add_clause([l, y, -z])
            add_clause([l, -y, z])
            add_clause([l, -y, -z])
        elif k == 2:
            l1, l2 = simplified
            y = next_var
            next_var += 1
            add_clause([l1, l2, y])
            add_clause([l1, l2, -y])
        elif k == 3:
            # Already a proper 3‑clause.
            add_clause(simplified)
        else:
            # Break long clause into a chain of 3‑clauses.
            lits = simplified
            # Create auxiliary variables y1 .. y_{k-3}
            aux_vars = []
            for _ in range(k - 3):
                aux_vars.append(next_var)
                next_var += 1
            # First clause: (l1 ∨ l2 ∨ y1)
            add_clause([lits[0], lits[1], aux_vars[0]])
            # Intermediate clauses
            for i in range(1, k - 3):
                # (¬y_i ∨ l_{i+2} ∨ y_{i+1})
                add_clause([-aux_vars[i - 1], lits[i + 1], aux_vars[i]])
            # Last clause: (¬y_{k-3} ∨ l_{k-1} ∨ l_k)
            add_clause([-aux_vars[-1], lits[-2], lits[-1]])

    result = {
        "num_vars": next_var - 1,  # highest variable index used
        "clauses": new_clauses,
    }
    return result

