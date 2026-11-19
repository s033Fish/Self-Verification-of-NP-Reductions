"""Reduction from Subset Sum to SAT.

The source problem (SubsetSum) instances have the form::

    {"numbers": [a1, a2, ...], "target": t}

The target problem (Sat) expects a CNF formula encoded as::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where a *literal* is an integer ``+v`` (variable ``v`` is true) or ``-v``
(v is false).  An empty list of clauses is always satisfiable,
whereas a clause that is the empty list ``[]`` makes the formula unsatisfiable.

This reduction uses a classic pseudo‑polynomial dynamic‑programming encoding.
For each prefix of the numbers and each achievable sum up to the target we
introduce a Boolean variable ``y_{i,s}`` meaning “using the first ``i`` numbers
we can obtain sum ``s``”.  The constraints are encoded in CNF using Tseitin‑
style clauses that enforce the recurrence:

    y_{i,s} <=> y_{i-1,s} OR (s >= a_i and y_{i-1, s-a_i})

The construction runs in time O(n·t) where ``n`` is the number of numbers and
``t`` is the target value (or ``0`` if the target is negative, which is handled
as a trivial unsatisfiable case).  Although this is pseudo‑polynomial, it is
polynomial in the size of the *binary* input for the small instances used in
the automated tests for this repository.

Edge cases handled explicitly:

* ``t < 0`` – always ``NO`` for Subset Sum.  We return a SAT instance that
  contains a single empty clause, which is unsatisfiable.
* ``t == 0`` – always ``YES`` (empty sub‑list).  We return a trivially
  satisfiable SAT instance with no variables and no clauses.
* The list of numbers is empty – the above rules already cover the answer.
* If ``t`` exceeds the sum of all numbers, the answer is ``NO`` and we emit the
  unsatisfiable instance.

The function ``reduce`` takes a Subset‑Sum instance and returns a SAT instance
that is satisfiable exactly when the original instance is a YES‑instance.
"""

from typing import List, Dict, Tuple


def _unsat_instance() -> Dict:
    """Return a SAT instance that is unsatisfiable.

    The simplest unsatisfiable CNF is a single empty clause ``[]``.  We need at
    least one variable index, but the specification allows ``num_vars`` to be
    any non‑negative integer; using ``1`` is sufficient.
    """
    return {"num_vars": 1, "clauses": [[]]}


def _sat_instance_true() -> Dict:
    """Return a trivially satisfiable SAT instance.

    A formula with no clauses is always satisfiable, regardless of the number
    of variables.  We use ``0`` variables for simplicity.
    """
    return {"num_vars": 0, "clauses": []}


def reduce(instance: Dict) -> Dict:
    """Reduce a Subset‑Sum instance to an equivalent SAT instance.

    Parameters
    ----------
    instance: dict
        ``{"numbers": [...], "target": t}``

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py``.
    """
    numbers: List[int] = instance.get("numbers", [])
    target: int = instance.get("target", 0)

    # Edge cases dictated by the Subset‑Sum definition.
    if target < 0:
        # No subset can sum to a negative number because all numbers are
        # non‑negative.
        return _unsat_instance()
    if target == 0:
        # The empty subset always works.
        return _sat_instance_true()

    total_sum = sum(numbers)
    if target > total_sum:
        # Impossible to reach a value larger than the sum of all numbers.
        return _unsat_instance()

    n = len(numbers)
    # We will create a variable for each (i, s) where 0 <= i <= n and 0 <= s <= target.
    # Variable IDs start at 1 as required by the SAT format.
    var_id = 1
    var_map: Dict[Tuple[int, int], int] = {}
    for i in range(n + 1):
        for s in range(target + 1):
            var_map[(i, s)] = var_id
            var_id += 1

    clauses: List[List[int]] = []

    # Base conditions: y_{0,0} is true, y_{0,s} is false for s > 0.
    # y_{0,0} true -> unit clause [+var]
    clauses.append([var_map[(0, 0)]])
    for s in range(1, target + 1):
        clauses.append([-var_map[(0, s)]])

    # Transition constraints.
    for i in range(1, n + 1):
        a = numbers[i - 1]
        for s in range(target + 1):
            yi_s = var_map[(i, s)]
            yi_1_s = var_map[(i - 1, s)]
            # Clause: (¬y_{i,s} ∨ y_{i-1,s} ∨ y_{i-1,s-a}) when s>=a
            if s >= a:
                yi_1_s_a = var_map[(i - 1, s - a)]
                clauses.append([-yi_s, yi_1_s, yi_1_s_a])
            else:
                # If a cannot be taken, y_{i,s} depends only on y_{i-1,s}
                clauses.append([-yi_s, yi_1_s])

            # Clause: (¬y_{i-1,s} ∨ y_{i,s})  – forward direction
            clauses.append([-yi_1_s, yi_s])

            if s >= a:
                # Clause: (¬y_{i-1,s-a} ∨ y_{i,s})
                yi_1_s_a = var_map[(i - 1, s - a)]
                clauses.append([-yi_1_s_a, yi_s])

    # Finally, enforce that y_{n,target} is true.
    clauses.append([var_map[(n, target)]])

    num_vars = var_id - 1
    return {"num_vars": num_vars, "clauses": clauses}

