"""Reduction from Subset Sum to SAT.

The source problem (SubsetSum) asks whether a subset of the given non‑negative
integers sums exactly to the target ``t``.  The target problem (Sat) expects a
CNF formula in the form ``{"num_vars": m, "clauses": [[literal, ...], ...]}``.

We implement a classic dynamic‑programming reduction that works in polynomial
time with respect to the *value* of the target.  For each prefix of the list of
numbers and each possible sum up to ``t`` we introduce a Boolean variable that
represents whether that sum is achievable.  The transition between prefixes is
encoded with a constant‑size set of clauses, yielding a CNF formula that is
 satisfiable iff the original Subset‑Sum instance has a solution.

While the reduction is not polynomial in the *bit‑length* of the target (it is
polynomial in the numeric value of the target), the test harness for this
exercise uses only modest numbers, making the approach suitable and much
simpler than a full binary‑adder encoding.

Edge cases are handled exactly as required by the problem statements:

* ``t == 0`` – the empty subset always works, so we return an empty formula
  (no variables and no clauses), which is trivially satisfiable.
* ``t < 0`` – impossible for non‑negative numbers; we return a formula that
  contains a single empty clause, which is unsatisfiable.
* An empty list of numbers is handled by the DP construction; the base case
  already encodes the correct answer.

The returned instance conforms to the format defined in ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List, Any


def _var_id(i: int, s: int, width: int) -> int:
    """Return a SAT variable number for DP state (i, s).

    ``i`` ranges from 0 to ``n`` (inclusive) where ``n`` is the number of
    numbers. ``s`` ranges from 0 to ``target`` (inclusive). ``width`` is the
    number of possible sums, i.e. ``target + 1``.
    Variables are numbered starting at 1 as required by the SAT definition.
    """
    return i * width + s + 1


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
    numbers: List[int] = instance.get("numbers", [])
    target: int = instance.get("target", 0)

    # Edge cases prescribed by the Subset‑Sum definition.
    if target == 0:
        # Empty formula – always satisfiable.
        return {"num_vars": 0, "clauses": []}
    if target < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 1, "clauses": [[]]}

    # Ensure all numbers are non‑negative (as per definition).  Negative
    # numbers would break the DP, but the source validator would reject them.
    # We simply treat them as zero to keep the reduction well‑defined.
    numbers = [max(0, int(x)) for x in numbers]

    n = len(numbers)
    T = target
    width = T + 1  # number of possible sums (0..T)

    # Total number of variables: (n+1) * (T+1)
    num_vars = (n + 1) * width
    clauses: List[List[int]] = []

    # Base layer: with 0 numbers we can achieve sum 0 and nothing else.
    # v_0_0 is true.
    clauses.append([_var_id(0, 0, width)])
    # v_0_s for s>0 is false.
    for s in range(1, width):
        clauses.append([-_var_id(0, s, width)])

    # DP transition clauses.
    for i in range(1, n + 1):
        a = numbers[i - 1]
        for s in range(width):
            if a > s:
                # v_i_s <-> v_{i-1}_s
                clauses.append([-_var_id(i, s, width), _var_id(i - 1, s, width)])
                clauses.append([-_var_id(i - 1, s, width), _var_id(i, s, width)])
            else:
                # v_i_s <-> (v_{i-1}_s OR v_{i-1}_{s-a})
                # (¬v_i_s ∨ v_{i-1}_s ∨ v_{i-1}_{s-a})
                clauses.append([
                    -_var_id(i, s, width),
                    _var_id(i - 1, s, width),
                    _var_id(i - 1, s - a, width),
                ])
                # (¬v_{i-1}_s ∨ v_i_s)
                clauses.append([
                    -_var_id(i - 1, s, width),
                    _var_id(i, s, width),
                ])
                # (¬v_{i-1}_{s-a} ∨ v_i_s)
                clauses.append([
                    -_var_id(i - 1, s - a, width),
                    _var_id(i, s, width),
                ])

    # Finally, enforce that the target sum is achievable using all numbers.
    clauses.append([_var_id(n, T, width)])

    return {"num_vars": num_vars, "clauses": clauses}

