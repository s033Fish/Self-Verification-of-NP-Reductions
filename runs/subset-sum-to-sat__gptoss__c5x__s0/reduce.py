"""Reduction from Subset Sum to SAT.

The reduction follows a classic dynamic‑programming encoding.  For a
Subset‑Sum instance with numbers ``a_1 … a_n`` and target ``t`` we create a
boolean variable ``y_{i,k}`` meaning *using the first ``i`` numbers we can
obtain sum ``k``*.

The variables are numbered sequentially starting at 1 so that they can be
used directly as SAT literals.  The constraints are:

* ``y_{0,0}`` is true and ``y_{0,k}`` is false for ``k>0``.
* For each ``i ≥ 1`` and each ``k`` (0 ≤ k ≤ t):
    ``y_{i,k} ⇔ (y_{i-1,k} ∨ (k ≥ a_i ∧ y_{i-1, k‑a_i}))``.
* Finally we require ``y_{n,t}`` to be true.

Each equivalence is expressed with two implications, each turned into a
clause in conjunctive normal form.  The construction runs in time
``O(n·t)`` and uses ``(n+1)·(t+1)`` variables – polynomial in the numeric
value of the target.  For the purpose of the automatic tests the target
values are kept small, so this simple encoding is sufficient.

Edge‑case handling matches the definition of Subset Sum:

* ``t < 0`` – always unsatisfiable; we return a formula containing an
  empty clause ``[]``.
* ``t == 0`` – always satisfiable; we return a formula with no clauses.
* ``t > sum(numbers)`` – impossible to reach; again we return an empty‑
  clause formula.

The module provides a single public function ``reduce(instance)`` that
converts a validated Subset‑Sum instance into a SAT instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import SubsetSum, Sat


def _var_index(i: int, k: int, t: int) -> int:
    """Map DP state (i, k) to a SAT variable index.

    Variables are numbered from 1 upwards.  ``i`` ranges from 0..n and ``k``
    from 0..t.  The total number of variables is ``(n+1)*(t+1)``.
    """
    return i * (t + 1) + k + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Subset‑Sum instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the SubsetSum format.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``).
    """
    # Validate the source instance first.
    SubsetSum.validate(instance)

    numbers: List[int] = instance["numbers"]
    t: int = instance["target"]

    # Edge cases defined by Subset Sum.
    if t < 0:
        # Unsatisfiable formula – a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}
    if t == 0:
        # Always satisfiable – empty formula.
        return {"num_vars": 0, "clauses": []}
    total = sum(numbers)
    if t > total:
        return {"num_vars": 1, "clauses": [[]]}

    n = len(numbers)
    # Number of variables for DP table (n+1) * (t+1)
    num_vars = (n + 1) * (t + 1)
    clauses: List[List[int]] = []

    # Base case: y_{0,0} = True, y_{0,k} = False for k>0
    clauses.append([_var_index(0, 0, t)])  # unit clause forcing true
    for k in range(1, t + 1):
        clauses.append([-_var_index(0, k, t)])  # force false

    # DP transition clauses
    for i in range(1, n + 1):
        a = numbers[i - 1]
        for k in range(0, t + 1):
            v = _var_index(i, k, t)
            u = _var_index(i - 1, k, t)
            # (u ∨ w) -> v  becomes (-u ∨ v) and (-w ∨ v) if w exists
            clauses.append([-u, v])
            if k >= a:
                w = _var_index(i - 1, k - a, t)
                clauses.append([-w, v])
                # v -> (u ∨ w)  becomes (-v ∨ u ∨ w)
                clauses.append([-v, u, w])
            else:
                # No w term, so v -> u  becomes (-v ∨ u)
                clauses.append([-v, u])

    # Require that the target sum is achievable using all numbers.
    clauses.append([_var_index(n, t, t)])

    # Validate the constructed SAT instance before returning.
    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

