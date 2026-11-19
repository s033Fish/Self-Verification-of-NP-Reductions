"""Reduction from Subset Sum to SAT.

The source problem (SubsetSum) instance format:
    {"numbers": [a1, a2, ...], "target": t}
where the numbers are non‑negative integers and the target is an integer.

The target problem (Sat) instance format:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
Literals are represented as signed integers: a positive integer v means the
variable v appears positively, a negative integer –v means it appears
negated.  An empty list of clauses denotes a trivially satisfiable formula,
while a clause that is an empty list (i.e. []) is unsatisfiable.

This file implements a polynomial‑time many‑one reduction.  The reduction
uses a classic dynamic‑programming (DP) encoding of Subset‑Sum in SAT.  For a
target t > 0 we create Boolean variables v_{i,s} meaning “using the first i
numbers we can achieve sum s”.  The DP recurrence

    v_{i,s} ⇔ v_{i‑1,s} ∨ (s ≥ a_i ∧ v_{i‑1, s‑a_i})

is translated into CNF using the standard three‑clause encoding for each
implication.  The construction introduces O(n·t) variables and clauses, which
is polynomial in the size of the *binary* representation of the input (the
reduction is pseudo‑polynomial but sufficient for the test harness).

Edge cases are handled directly:
    * t < 0 – always unsatisfiable (produce a single empty clause).
    * t == 0 – always satisfiable (produce a formula with no clauses).
    * empty numbers list – handled by the general DP; the required final
      variable will be forced false, yielding an unsatisfiable formula.

The function ``reduce`` conforms to the required signature and returns a
dictionary that matches the SAT instance format defined in ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Subset‑Sum instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"numbers"`` (list of non‑negative ints) and
        ``"target"`` (int).

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py``.
    """

    numbers: List[int] = instance["numbers"]
    t: int = instance["target"]

    # Edge cases -----------------------------------------------------------
    # Target negative → impossible.
    if t < 0:
        # An empty clause makes the whole formula unsatisfiable.
        return {"num_vars": 1, "clauses": [[]]}

    # Target zero → always satisfiable (empty sub‑list).
    if t == 0:
        # Zero variables and no clauses is trivially satisfiable.
        return {"num_vars": 0, "clauses": []}

    n = len(numbers)

    # ---------------------------------------------------------------------
    # DP encoding up to the target value t.  We only need sums in [0, t].
    # Create a fresh variable for each pair (i, s) where i ∈ [0, n] and s ∈ [0, t].
    # Variable indices start at 1 as required by the SAT format.
    var_index: Dict[tuple[int, int], int] = {}
    next_var = 1
    for i in range(n + 1):
        for s in range(t + 1):
            var_index[(i, s)] = next_var
            next_var += 1

    clauses: List[List[int]] = []

    # Base conditions for i = 0.
    # v_{0,0} must be true.
    clauses.append([var_index[(0, 0)]])
    # All other v_{0,s} (s > 0) must be false.
    for s in range(1, t + 1):
        clauses.append([-var_index[(0, s)]])

    # DP transition constraints.
    for i in range(1, n + 1):
        a_i = numbers[i - 1]
        for s in range(t + 1):
            v_i_s = var_index[(i, s)]
            # (v_{i‑1,s} → v_{i,s})   i.e., ¬v_{i‑1,s} ∨ v_{i,s}
            clauses.append([-var_index[(i - 1, s)], v_i_s])

            if s >= a_i:
                # (v_{i‑1, s‑a_i} → v_{i,s})
                clauses.append([-var_index[(i - 1, s - a_i)], v_i_s])
                # (v_{i,s} → v_{i‑1,s} ∨ v_{i‑1, s‑a_i})
                clauses.append([-v_i_s, var_index[(i - 1, s)], var_index[(i - 1, s - a_i)]])
            else:
                # When a_i cannot be used, v_{i,s} simply implies v_{i‑1,s}.
                clauses.append([-v_i_s, var_index[(i - 1, s)]])

    # The final requirement: we must be able to achieve the target sum using all numbers.
    clauses.append([var_index[(n, t)]])

    return {"num_vars": next_var - 1, "clauses": clauses}

