"""Reduction from 1-in-3 SAT (positive) to Subset Sum.

The source problem ``OneInThreeSat`` is defined by an instance of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where each clause contains three *different* positive variable indices.
The formula is satisfiable iff we can assign each variable a Boolean value
such that **exactly one** variable in every clause evaluates to ``True``.

The target problem ``SubsetSum`` expects an instance::

    {"numbers": [a1, a2, ...], "target": t}

and asks whether a sub‑multiset of ``numbers`` sums to ``t``.

The reduction encodes a truth assignment as a selection of numbers – one
choice for each variable (the *true* number or the *false* number).  Digits
in a large base ``B`` are used to avoid carries between independent parts of
the encoding.

Encoding details (polynomial time, deterministic):

* Let ``n`` be the number of clauses and ``m`` the number of variables.
* Choose a base ``B = 4``.  ``B`` is larger than the maximum possible digit
  sum (which is at most 3 for clause‑digits and 2 for variable‑digits), so
  addition in base ``B`` never creates carries.
* The integer representation consists of ``n + m`` digit positions:
    - Positions ``0 .. n-1`` correspond to clauses.
    - Positions ``n .. n+m-1`` correspond to variables.
* For each variable ``i`` (1‑based) we create two numbers:
    - ``true_i``  : contributes ``1`` to every clause‑digit where ``i``
      appears, and ``1`` to its own variable‑digit.
    - ``false_i`` : contributes ``0`` to all clause‑digits and ``1`` to the
      same variable‑digit.
  Selecting exactly one of the two numbers for each variable forces the
  variable‑digit sum to be ``1`` (the target requires ``1`` there) and also
  ensures that the clause‑digit sum equals the number of true literals in
  that clause.
* The target integer has digit ``1`` in every clause‑position (enforcing that
  exactly one literal per clause is true) and digit ``1`` in every variable
  position (enforcing that exactly one of the two numbers per variable is
  chosen).

Correctness sketch:
    *If the SAT instance is satisfiable*, pick ``true_i`` for variables set
    to ``True`` and ``false_i`` otherwise.  Clause‑digits sum to exactly one
    because each clause has exactly one true literal.  Variable‑digits sum to
    one because exactly one of the two numbers per variable is chosen.
    The total sum equals the target.
    *Conversely*, any subset that sums to the target must have digit ``1``
    in every variable‑position, which is only possible by selecting exactly
    one of the two numbers for each variable.  The clause‑digits then count
    how many of the three literals in each clause are true; the target
    requires this count to be ``1``.  Hence the corresponding assignment
    satisfies the original formula.

The implementation below follows this construction.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a ``OneInThreeSat`` instance to a ``SubsetSum`` instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[a, b, c], ...]}``

    Returns
    -------
    dict
        ``{"numbers": [...], "target": t}`` suitable for the SubsetSum
        problem.
    """

    # Extract data
    m: int = int(instance.get("num_vars", 0))
    clauses: List[List[int]] = instance.get("clauses", [])
    n: int = len(clauses)

    # Base large enough to avoid carries (max digit sum < B)
    B: int = 4

    # Map each variable to the set of clause indices it appears in
    var_to_clauses: List[List[int]] = [[] for _ in range(m + 1)]  # 1‑based
    for idx, clause in enumerate(clauses):
        for var in clause:
            # The problem guarantees that variables are within 1..m
            if 1 <= var <= m:
                var_to_clauses[var].append(idx)
            else:
                # Defensive: ignore out‑of‑range variables (should not happen)
                continue

    numbers: List[int] = []

    # For each variable create the true and false numbers
    for var in range(1, m + 1):
        # Position of the variable‑digit (0‑based exponent)
        var_pos = n + (var - 1)
        var_weight = B ** var_pos

        # True number: contributes to clause digits where the variable occurs
        true_num = var_weight
        for clause_idx in var_to_clauses[var]:
            true_num += B ** clause_idx
        # False number: contributes only the variable digit
        false_num = var_weight

        numbers.append(true_num)
        numbers.append(false_num)

    # Construct target: digit 1 for each clause and each variable
    target = 0
    for clause_idx in range(n):
        target += B ** clause_idx
    for var in range(m):
        target += B ** (n + var)

    return {"numbers": numbers, "target": target}

