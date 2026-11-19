"""Reduction from 3‑SAT to Subset Sum.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.  Each
clause contains exactly three literals on distinct variables; a literal is
represented by a signed integer ``+v`` (variable ``v`` is true) or ``-v``
(variable ``v`` is false).

The target problem is ``SubsetSum`` with instance format ``{"numbers":
[a1, a2, ...], "target": t}``.

We implement the classic textbook polynomial‑time reduction.  Let ``m`` be the
number of variables and ``n`` the number of clauses.  Choose a base ``B = n +
1``.  For each variable ``i`` (1‑based) we create two numbers, one representing
the assignment *true* and one representing *false*:

* Both numbers have a digit ``1`` in the *variable* position ``i`` (the ``i``‑th
  digit when the number is expressed in base ``B``).  This forces any valid
  subset to pick exactly one of the two numbers for each variable because the
  target also contains exactly one in each variable position.
* Additionally, a number contains a digit ``1`` in clause position ``j`` (the
  ``m + j``‑th digit) for every clause ``j`` that the corresponding literal
  satisfies.

The target sum therefore has digit ``1`` in every variable position and digit
``1`` in every clause position.  Because the base ``B`` is larger than the
maximum possible sum of clause digits (at most three literals per clause), no
carry occurs between digits.  Consequently a subset sums to the target iff the
chosen literals (one per variable) make exactly one literal true in each clause,
which is equivalent to the original 3‑SAT formula being satisfiable.

The reduction runs in time polynomial in ``m`` and ``n`` and uses only
integer arithmetic.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        lists of ints) as described in the problem statement.

    Returns
    -------
    dict
        A Subset‑Sum instance ``{"numbers": [...], "target": t}``.
    """

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    n: int = len(clauses)

    # Base larger than the maximum number of literals that can contribute to a
    # clause digit (which is at most 3).  Using n+1 guarantees no carries.
    B: int = n + 1 if n > 0 else 2  # for the edge case of zero clauses

    numbers: List[int] = []

    # Pre‑compute which literals appear in each clause for quick lookup.
    # For each variable i we store two boolean lists indicating presence of the
    # positive and negative literal in each clause.
    pos_in_clause = [ [False] * n for _ in range(m) ]
    neg_in_clause = [ [False] * n for _ in range(m) ]
    for j, clause in enumerate(clauses):
        for lit in clause:
            var = abs(lit) - 1  # zero‑based index
            if lit > 0:
                pos_in_clause[var][j] = True
            else:
                neg_in_clause[var][j] = True

    # Construct numbers for each variable assignment.
    for i in range(m):
        # True literal number
        true_val = B ** i  # digit 1 at variable position i
        for j in range(n):
            if pos_in_clause[i][j]:
                true_val += B ** (m + j)
        numbers.append(true_val)

        # False literal number
        false_val = B ** i
        for j in range(n):
            if neg_in_clause[i][j]:
                false_val += B ** (m + j)
        numbers.append(false_val)

    # Build the target sum: digit 1 in each variable position and each clause
    # position.
    target = 0
    for i in range(m):
        target += B ** i
    for j in range(n):
        target += B ** (m + j)

    return {"numbers": numbers, "target": target}

