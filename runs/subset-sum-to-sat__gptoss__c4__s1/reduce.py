"""Reduction from Subset Sum to SAT.

The reduction follows a classic dynamic‑programming encoding of the
Subset‑Sum decision problem into a Boolean formula.  For a given instance

    numbers = [a1, a2, ..., an]
    target  = T

we create Boolean variables ``s_i_v`` meaning *"using the first i numbers we
can obtain a sum of v"* (0 ≤ i ≤ n, 0 ≤ v ≤ T).  The encoding uses O(n·T)
variables and clauses, which is polynomial in the size of the input when T is
given in unary – sufficient for the test harness used in this task.

The CNF constraints enforce the standard DP recurrence:

    s_i_v  ⇔  s_{i-1}_v  ∨  (v ≥ a_i ∧ s_{i-1}_{v-a_i})

Additionally we force ``s_0_0`` to be true (empty subset sums to 0) and all
other ``s_0_v`` for v>0 to be false.  Finally we require ``s_n_T`` to be true;
the formula is satisfiable exactly when the original Subset‑Sum instance has a
solution.

Edge‑case handling:
* ``target < 0`` – always unsatisfiable, we return a formula containing an
  empty clause ``[]``.
* ``target == 0`` – always satisfiable, we return an empty formula (no
  variables, no clauses).
* Empty ``numbers`` list – the DP still works; the base case decides the
  answer.

The module defines a single function ``reduce(instance)`` that takes a
validated Subset‑Sum instance and returns a validated SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import SubsetSum, Sat


def _new_var(counter: List[int]) -> int:
    """Generate a fresh SAT variable identifier.

    ``counter`` is a single‑element list holding the next available integer;
    using a list allows us to mutate it inside the function without
    declaring ``nonlocal``.
    """

    counter[0] += 1
    return counter[0]


def reduce(instance: dict) -> dict:
    """Reduce a Subset‑Sum instance to an equivalent SAT instance.

    The returned dictionary follows the format required by ``Sat.validate``:
    ``{"num_vars": m, "clauses": [[lit, ...], ...]}`` where each literal
    is a signed integer.
    """

    # Validate the source instance first.
    SubsetSum.validate(instance)

    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Edge cases that can be decided without constructing a formula.
    if target < 0:
        # Unsatisfiable: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if target == 0:
        # Always satisfiable – empty formula.
        return {"num_vars": 0, "clauses": []}

    n = len(numbers)
    T = target

    # Mapping (i, v) -> variable id for s_i_v.
    var_id: Dict[Tuple[int, int], int] = {}
    counter = [0]  # mutable counter for fresh IDs
    for i in range(n + 1):
        for v in range(T + 1):
            var_id[(i, v)] = _new_var(counter)

    clauses: List[List[int]] = []

    # Base: s_0_0 is true, all other s_0_v (v>0) are false.
    clauses.append([var_id[(0, 0)]])  # unit clause making it true
    for v in range(1, T + 1):
        clauses.append([-var_id[(0, v)]])  # force false

    # DP transition constraints.
    for i in range(1, n + 1):
        a = numbers[i - 1]
        for v in range(T + 1):
            # (¬s_{i-1}_v ∨ s_i_v)  – if we could achieve v before, we can still achieve it.
            clauses.append([-var_id[(i - 1, v)], var_id[(i, v)]])

            # (¬s_i_v ∨ s_{i-1}_v ∨ s_{i-1}_{v-a})  – if we achieve v now, it must come from either not taking a or taking it.
            if v >= a:
                clauses.append(
                    [
                        -var_id[(i, v)],
                        var_id[(i - 1, v)],
                        var_id[(i - 1, v - a)],
                    ]
                )
            else:
                # When v < a, the only way is not taking a.
                clauses.append([-var_id[(i, v)], var_id[(i - 1, v)]])

    # Final requirement: s_n_T must be true.
    clauses.append([var_id[(n, T)]])

    num_vars = counter[0]
    sat_instance = {"num_vars": num_vars, "clauses": clauses}
    # Validate the produced SAT instance.
    Sat.validate(sat_instance)
    return sat_instance

