"""Reduction from SAT to 3‑SAT.

Implements a polynomial‑time many‑one reduction from the general CNF SAT
problem (``Sat``) to the restricted version where every clause has exactly
three literals on distinct variables (``ThreeSat``).

The reduction follows the classic textbook construction:

* **Simplify each clause** – remove duplicate literals and drop tautological
  clauses (those containing a variable together with its negation).  The
  remaining literals are all on distinct variables.
* For a clause of length ``k`` after simplification:
    - ``k == 0`` – the original formula is unsatisfiable.  We replace the
      whole instance by a fixed unsatisfiable 3‑SAT core that forces a fresh
      variable to be both true and false using the unit‑clause gadget.
    - ``k == 1`` – a unit clause ``l``.  The gadget

          (l ∨ a ∨ b) ∧ (l ∨ a ∨ ¬b) ∧ (l ∨ ¬a ∨ b) ∧ (l ∨ ¬a ∨ ¬b)

      (with fresh ``a`` and ``b``) is equivalent to the unit clause.
    - ``k == 2`` – a binary clause ``l₁ ∨ l₂``.  Introducing a fresh variable
      ``y`` we replace it by the pair ``(l₁ ∨ l₂ ∨ y) ∧ (l₁ ∨ l₂ ∨ ¬y)``.
    - ``k >= 3`` – we break the clause into a chain of 3‑literal clauses
      using fresh auxiliary variables ``y₁, y₂, …``:

          (l₁ ∨ l₂ ∨ y₁)
          (¬y₁ ∨ l₃ ∨ y₂)
          …
          (¬y_{k‑3} ∨ l_{k‑1} ∨ l_k)

      This construction preserves satisfiability and respects the 3‑SAT
      format (all literals in a clause refer to distinct variables).

The algorithm runs in time polynomial in the size of the input formula –
we introduce at most a constant number of fresh variables per original
literal.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Sat, ThreeSat


def _fresh_var(counter: List[int]) -> int:
    """Return a fresh variable index and increment the counter.

    ``counter`` is a one‑element list storing the next available variable
    number.  Using a mutable container avoids the need for ``nonlocal``.
    """

    v = counter[0]
    counter[0] += 1
    return v


def _simplify_clause(clause: List[int]) -> List[int] | None:
    """Simplify a clause.

    Removes duplicate literals and returns ``None`` if the clause is a
    tautology (contains both ``v`` and ``-v``).  The returned list contains
    each variable at most once, preserving any sign.
    """

    seen: Dict[int, int] = {}
    for lit in clause:
        var = abs(lit)
        sign = 1 if lit > 0 else -1
        if var in seen:
            if seen[var] != sign:
                # Tautology – the clause is always satisfied.
                return None
            # Duplicate with same sign – ignore.
        else:
            seen[var] = sign
    return [sign * var for var, sign in seen.items()]


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance conforms to ``ThreeSat``'s format.
    """

    # Validate source instance.
    Sat.validate(instance)

    num_vars = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    # Fresh variable counter starts after the original variables.
    next_var = [num_vars + 1]
    new_clauses: List[List[int]] = []

    def _add_unsat_core() -> None:
        """Add a small unsatisfiable 3‑SAT sub‑formula.

        Uses the unit‑clause gadget on a fresh variable forced both true and
        false, guaranteeing the whole formula is unsatisfiable.
        """

        v = _fresh_var(next_var)
        # Force v true.
        a = _fresh_var(next_var)
        b = _fresh_var(next_var)
        new_clauses.extend([
            [v, a, b],
            [v, a, -b],
            [v, -a, b],
            [v, -a, -b],
        ])
        # Force v false (i.e., -v true) using the same gadget.
        a2 = _fresh_var(next_var)
        b2 = _fresh_var(next_var)
        new_clauses.extend([
            [-v, a2, b2],
            [-v, a2, -b2],
            [-v, -a2, b2],
            [-v, -a2, -b2],
        ])

    for clause in original_clauses:
        simplified = _simplify_clause(clause)
        if simplified is None:
            # Tautology – can be ignored.
            continue
        k = len(simplified)
        if k == 0:
            # Empty clause – unsatisfiable formula.
            _add_unsat_core()
            continue
        if k == 1:
            (l,) = simplified
            a = _fresh_var(next_var)
            b = _fresh_var(next_var)
            new_clauses.extend([
                [l, a, b],
                [l, a, -b],
                [l, -a, b],
                [l, -a, -b],
            ])
        elif k == 2:
            l1, l2 = simplified
            y = _fresh_var(next_var)
            new_clauses.append([l1, l2, y])
            new_clauses.append([l1, l2, -y])
        else:
            # k >= 3 – chain construction.
            lits = simplified
            # First clause with fresh y1.
            y_prev = _fresh_var(next_var)
            new_clauses.append([lits[0], lits[1], y_prev])
            # Intermediate clauses.
            for i in range(2, k - 1):
                y_curr = _fresh_var(next_var)
                new_clauses.append([-y_prev, lits[i], y_curr])
                y_prev = y_curr
            # Last clause.
            new_clauses.append([-y_prev, lits[-2], lits[-1]])

    final_num_vars = next_var[0] - 1
    result = {"num_vars": final_num_vars, "clauses": new_clauses}
    ThreeSat.validate(result)
    return result

