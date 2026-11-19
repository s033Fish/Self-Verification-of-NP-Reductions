"""Reduction from SAT to 3‑SAT.

The source problem (SAT) allows clauses of arbitrary length (including
empty clauses) and may contain duplicate literals or both a literal and its
negation.  The target problem (ThreeSat) requires each clause to contain
exactly three *distinct* variables and must not contain a variable together
with its negation.

The reduction preserves satisfiability:

* An empty clause in the SAT instance makes the formula unsatisfiable.  We
  return a fixed unsatisfiable 3‑SAT instance that uses three fresh variables
  and the eight possible 3‑literal clauses – this combination is well‑known
  to be unsatisfiable.
* A formula with no clauses is always satisfiable; we return a 3‑SAT instance
  with zero clauses (allowed by the specification).
* For each non‑tautological clause we transform it into an equivalent set of
  3‑literal clauses using fresh auxiliary variables.  The construction is
  standard and works in polynomial time.

The helper ``_next_var`` generates fresh variable indices that do not clash
with the original variables.  ``_normalize`` removes duplicate literals and
detects tautological clauses (containing both *v* and *‑v*), which can be
safely omitted because they are always satisfied.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance follows the format described in ``problems.py``
    for ``ThreeSat``:

    ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
    """

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def _next_var() -> int:
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    def _normalize(cl: List[int]) -> List[int] | None:
        """Return a list of literals with distinct variables.

        If the clause contains both a literal and its negation, it is a
        tautology and the function returns ``None`` to indicate the clause can
        be omitted.
        """
        seen: Dict[int, bool] = {}
        for lit in cl:
            var = abs(lit)
            sign = lit > 0
            if var in seen:
                if seen[var] != sign:
                    # contains both v and -v -> always true
                    return None
                # duplicate literal with same sign – ignore
            else:
                seen[var] = sign
        # Build list preserving any order (order does not matter)
        return [var if sign else -var for var, sign in seen.items()]

    # ------------------------------------------------------------------
    # Begin reduction
    # ------------------------------------------------------------------
    num_vars = int(instance.get("num_vars", 0))
    clauses: List[List[int]] = instance.get("clauses", [])

    # Edge case: formula with no clauses is trivially satisfiable.
    if not clauses:
        # Any number of variables is fine; keep the original count.
        return {"num_vars": max(num_vars, 0), "clauses": []}

    # Detect an empty clause – makes the whole formula unsatisfiable.
    for cl in clauses:
        if len(cl) == 0:
            # Return a fixed unsatisfiable 3‑SAT instance on three variables.
            unsat_clauses = []
            vars3 = [1, 2, 3]
            # All 8 possible clauses on three distinct variables.
            for a in (vars3[0], -vars3[0]):
                for b in (vars3[1], -vars3[1]):
                    for c in (vars3[2], -vars3[2]):
                        unsat_clauses.append([a, b, c])
            return {"num_vars": 3, "clauses": unsat_clauses}

    # Normal processing – transform each clause.
    next_var = num_vars + 1  # fresh variable counter
    new_clauses: List[List[int]] = []

    for cl in clauses:
        norm = _normalize(cl)
        if norm is None:
            # Tautology – clause always satisfied; skip it.
            continue
        k = len(norm)
        if k == 0:
            # Should not happen (empty clause already handled), but treat as unsat.
            continue
        if k == 1:
            # Single literal l -> use two fresh vars u,v and four clauses covering
            # all assignments to (u,v). This forces l to be true.
            l = norm[0]
            u = _next_var()
            v = _next_var()
            new_clauses.extend([
                [l, u, v],
                [l, u, -v],
                [l, -u, v],
                [l, -u, -v],
            ])
        elif k == 2:
            # Two literals l1,l2 -> introduce fresh u and add (l1,l2,u) and (l1,l2,-u).
            l1, l2 = norm
            u = _next_var()
            new_clauses.append([l1, l2, u])
            new_clauses.append([l1, l2, -u])
        elif k == 3:
            # Already size three with distinct variables – keep as is.
            new_clauses.append(norm)
        else:
            # k > 3 – use the standard chain construction.
            # Create auxiliary variables y1..y_{k-3}
            literals = norm
            # First clause: (l1 ∨ l2 ∨ y1)
            y_prev = _next_var()
            new_clauses.append([literals[0], literals[1], y_prev])
            # Middle clauses
            for i in range(2, k - 2):
                y_cur = _next_var()
                new_clauses.append([-y_prev, literals[i], y_cur])
                y_prev = y_cur
            # Last clause: (¬y_{k-3} ∨ l_{k-1} ∨ l_k)
            new_clauses.append([-y_prev, literals[-2], literals[-1]])

    # If after processing we ended up with no clauses, the formula is trivially
    # satisfiable – return an empty 3‑SAT instance.
    if not new_clauses:
        return {"num_vars": max(next_var - 1, 0), "clauses": []}

    return {"num_vars": next_var - 1, "clauses": new_clauses}

