"""Reduction from 3‑SAT to Subset Sum.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
following instance format::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Each literal ``l`` is an integer ``+v`` (meaning variable *v* is true) or
``-v`` (meaning variable *v* is false).  Every clause contains exactly three
different variables.

The target problem is ``SubsetSum`` with instance format::

    {"numbers": [a1, a2, ...], "target": t}

We implement the classic polynomial‑time reduction described in many textbooks:

* Let ``n`` be the number of clauses and ``m`` the number of variables.
* Choose a base ``B = n + 1``.  Because each digit of a number is at most ``1``
  (the construction never creates a digit larger than ``1``), using a base
  larger than the maximum possible sum of digits guarantees that no carries
  occur when we add the numbers.
* For each variable ``i`` (1‑based) we create two numbers – one representing the
  assignment ``x_i = True`` and the other ``x_i = False``.  The number has two
  groups of digits:

  - **Variable‑selection digits**: the ``i``‑th digit (0‑based) is set to ``1``
    in *both* numbers.  This forces the subset‑sum solution to pick exactly one
    of the two numbers for each variable, because the target requires a digit
    sum of ``1`` in each of these positions.
  - **Clause‑satisfaction digits**: for each clause ``j`` (0‑based) we set the
    digit at position ``m + j`` to ``1`` if the literal satisfied by the current
    assignment appears in clause ``j``; otherwise the digit is ``0``.

* The target number has digit ``1`` in every variable‑selection position and
  digit ``1`` in every clause‑satisfaction position.  Consequently a subset of
  numbers sums to the target iff the chosen literals (one per variable) satisfy
  every clause.

Edge cases:
    * If there are **no clauses** (``n == 0``) the formula is trivially
      satisfiable.  We return the empty list of numbers with target ``0`` – the
      Subset Sum instance is a guaranteed *yes*.
    * The construction works for ``m == 0`` as well (the empty formula is
      satisfiable).  In that case ``n`` must also be ``0`` and the same empty
      instance is returned.

The function runs in time polynomial in ``m`` and ``n`` and uses only integer
arithmetic.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _literal_satisfied_by_true(var: int, clause: List[int]) -> bool:
    """Return ``True`` if the literal ``+var`` appears in *clause*.

    ``clause`` is a list of three integers representing literals.
    """
    return var in clause


def _literal_satisfied_by_false(var: int, clause: List[int]) -> bool:
    """Return ``True`` if the literal ``-var`` appears in *clause*.
    """
    return -var in clause


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"numbers": [...], "target": t}`` suitable for the SubsetSum
        solver.
    """

    m: int = int(instance.get("num_vars", 0))
    clauses: List[List[int]] = list(instance.get("clauses", []))
    n: int = len(clauses)

    # Edge case: no clauses → trivially satisfiable.
    if n == 0:
        return {"numbers": [], "target": 0}

    # Base larger than any possible digit sum to avoid carries.
    B: int = n + 1

    numbers: List[int] = []

    # Pre‑compute powers of B for efficiency.
    # Positions 0 .. m-1 : variable selection digits
    # Positions m .. m+n-1 : clause digits
    pow_B: List[int] = [1]
    for _ in range(m + n):
        pow_B.append(pow_B[-1] * B)

    # Build numbers for each variable.
    for var in range(1, m + 1):
        # Number representing var = True
        num_true = pow_B[var - 1]  # variable‑selection digit = 1
        # Add clause digits where +var appears.
        for idx, clause in enumerate(clauses):
            if _literal_satisfied_by_true(var, clause):
                num_true += pow_B[m + idx]
        numbers.append(num_true)

        # Number representing var = False
        num_false = pow_B[var - 1]
        for idx, clause in enumerate(clauses):
            if _literal_satisfied_by_false(var, clause):
                num_false += pow_B[m + idx]
        numbers.append(num_false)

    # Construct target: digit 1 in every variable‑selection position and
    # digit 1 in every clause position.
    target = 0
    for i in range(m):
        target += pow_B[i]
    for j in range(n):
        target += pow_B[m + j]

    return {"numbers": numbers, "target": target}

