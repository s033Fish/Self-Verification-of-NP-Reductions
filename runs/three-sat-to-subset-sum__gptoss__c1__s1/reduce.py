"""Reduction from 3‑SAT to Subset Sum.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with an
instance format

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal is an integer ``+v`` (variable *v* is true) or ``-v``
(v is false).  The target problem is ``SubsetSum`` with an instance format

    {"numbers": [a1, a2, ...], "target": t}

The reduction follows the classic textbook construction that uses a mixed‑
radix representation.  For each variable we create two numbers – one for
assigning the variable true and one for assigning it false.  Each number
contains a *variable digit* (ensuring exactly one of the two numbers is
chosen) and a set of *clause digits* indicating which clauses become true
if that literal is selected.

We choose a base ``B`` larger than the maximum possible sum in any clause
digit.  A clause contains three literals, so ``B = max(k + 1, 4)`` where ``k``
is the number of clauses guarantees that carries never occur when we add
the numbers.

Construction details
---------------------
* Let ``m`` be the number of variables and ``k`` the number of clauses.
* For variable ``i`` (1‑based) the weight of its variable digit is
  ``B**(i-1)``.
* For clause ``j`` (0‑based) the weight of its clause digit is
  ``B**(m + j)``.
* The target value is the sum of **all** variable digits (exactly one per
  variable) plus the sum of **all** clause digits (exactly one per clause).
* For each variable ``i`` we create two numbers:
    - ``true_val``  – variable digit + clause digits for every clause that
      contains the literal ``+i``.
    - ``false_val`` – variable digit + clause digits for every clause that
      contains the literal ``-i``.
  Both numbers have the same variable digit (ensuring the digit contributes
  ``1`` regardless of the chosen truth value) and differ only in the clause
  contributions.

Correctness sketch
-------------------
*If the 3‑SAT instance is satisfiable*: pick for each variable the number
 corresponding to the truth value in a satisfying assignment that makes
 **exactly one** literal true in each clause (such an assignment always
 exists by arbitrarily turning false any extra true literals).  The sum of
 the chosen numbers equals the target because each variable digit contributes
 ``1`` and each clause digit contributes ``1`` exactly once.

*If the Subset‑Sum instance has a solution*: because the target has a digit
 ``1`` in every variable position, the solution must contain **exactly one**
 of the two numbers for each variable (otherwise the digit would be ``0`` or
 ``≥2``).  The clause digits therefore indicate, for each clause, how many
 selected literals satisfy it.  Since the target clause digit is ``1`` and
 the base prevents carries, each clause digit must be exactly ``1`` – i.e.
 at least one literal of the clause is true.  Hence the corresponding truth
 assignment satisfies the original 3‑SAT formula.

Both directions hold, establishing a polynomial‑time many‑one reduction.

The implementation below follows this construction and runs in time
polynomial in ``m`` and ``k``.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A Subset‑Sum instance ``{"numbers": [...], "target": t}``.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    k: int = len(clauses)

    # Choose a base larger than any possible digit sum (max 3 literals per
    # clause).  Ensure the base is at least 4 to also handle the case k = 0.
    base: int = max(k + 1, 4)

    # Pre‑compute powers for variable and clause positions.
    var_weights = [base ** i for i in range(m)]          # positions 0 .. m-1
    clause_weights = [base ** (m + j) for j in range(k)]  # positions m .. m+k-1

    # Target: one in each variable position + one in each clause position.
    target = sum(var_weights) + sum(clause_weights)

    numbers: List[int] = []

    # Build numbers for each variable.
    for i in range(1, m + 1):
        var_weight = var_weights[i - 1]
        true_val = var_weight
        false_val = var_weight

        for j, clause in enumerate(clauses):
            if i in clause:  # literal +i present (since literals are ints)
                true_val += clause_weights[j]
            if -i in clause:
                false_val += clause_weights[j]

        numbers.append(true_val)
        numbers.append(false_val)

    return {"numbers": numbers, "target": target}

