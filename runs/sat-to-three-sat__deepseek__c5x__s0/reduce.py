"""Polynomial-time reduction from SAT to 3-SAT.

Source: SAT with clauses of arbitrary length (possibly empty, with repeated
literals, or tautological).  Target: 3-SAT where every clause has exactly
three literals on three different variables.

The reduction is the standard one:

* A clause that is a tautology (contains both v and -v) is dropped.
* After removing duplicate literals, a clause with k distinct literals is
  handled by cases:

  - k == 0: emit an unsatisfiable block (all 8 clauses over 3 fresh vars).
  - k == 1: (l) becomes four clauses over l and two fresh vars z1, z2.
  - k == 2: (l1 v l2) becomes two clauses over l1, l2 and one fresh var z.
  - k == 3: already a valid 3-clause.
  - k >= 4: split with k-3 fresh linking variables.

Fresh variables are numbered m+1, m+2, ... and never collide with the
original variables, so every produced clause uses three distinct variables.
"""

from __future__ import annotations

from typing import Any


def _dedupe(clause: list[int]) -> list[int]:
    """Remove duplicate literals while preserving order."""
    seen: set[int] = set()
    out: list[int] = []
    for literal in clause:
        if literal not in seen:
            seen.add(literal)
            out.append(literal)
    return out


def _is_tautology(literals: list[int]) -> bool:
    """True iff the clause contains both v and -v for some variable."""
    seen: set[int] = set()
    for literal in literals:
        if -literal in seen:
            return True
        seen.add(literal)
    return False


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a SAT instance to an equisatisfiable 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = num_vars

    def fresh() -> int:
        nonlocal next_var
        next_var += 1
        return next_var

    out_clauses: list[list[int]] = []

    for clause in clauses:
        literals = _dedupe(clause)

        # Tautologies are always satisfied and can be removed.
        if _is_tautology(literals):
            continue

        k = len(literals)

        if k == 0:
            # Empty clause: unsatisfiable.  Emit all 8 clauses over 3 fresh
            # variables, which is unsatisfiable and keeps num_vars >= 3.
            a, b, c = fresh(), fresh(), fresh()
            for sa in (a, -a):
                for sb in (b, -b):
                    for sc in (c, -c):
                        out_clauses.append([sa, sb, sc])
        elif k == 1:
            (l1,) = literals
            z1, z2 = fresh(), fresh()
            out_clauses.append([l1, z1, z2])
            out_clauses.append([l1, z1, -z2])
            out_clauses.append([l1, -z1, z2])
            out_clauses.append([l1, -z1, -z2])
        elif k == 2:
            l1, l2 = literals
            z = fresh()
            out_clauses.append([l1, l2, z])
            out_clauses.append([l1, l2, -z])
        elif k == 3:
            out_clauses.append(list(literals))
        else:
            # k >= 4: chain of clauses with k-3 fresh linking variables.
            y = [fresh() for _ in range(k - 3)]
            out_clauses.append([literals[0], literals[1], y[0]])
            for i in range(1, k - 3):
                out_clauses.append([-y[i - 1], literals[i + 1], y[i]])
            out_clauses.append([-y[k - 4], literals[k - 2], literals[k - 1]])

    return {"num_vars": next_var, "clauses": out_clauses}
