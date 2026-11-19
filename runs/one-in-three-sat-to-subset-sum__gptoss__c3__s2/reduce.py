"""Reduction from 1-in-3-SAT (positive) to Subset Sum.

The source problem instance format is defined by ``OneInThreeSat`` in
``problems.py``:

    {"num_vars": m, "clauses": [[a, b, c], ...]}

All literals are positive variable indices (1‑based) and each clause has three
distinct variables.

The target problem is Subset Sum with format:

    {"numbers": [a1, a2, ...], "target": t}

We use the classic base‑encoding reduction.  Choose a base ``B = 4`` which is
strictly larger than the maximum possible sum contributed to any clause digit
(at most three true variables).  For each clause we reserve a digit position
``B**j`` (where ``j`` is the clause index).  For each variable we create a
number that has a ``1`` in every digit corresponding to a clause that contains
that variable.  Selecting a variable's number in the subset corresponds to
setting the variable to *true*.

The target sum has a digit ``1`` in every clause position, i.e. ``sum_{j=0}^{C-1}
B**j`` where ``C`` is the number of clauses.  Because ``B`` is larger than the
maximum per‑digit contribution, the only way to reach the target is to pick
exactly one variable from each clause – which is precisely a satisfying
assignment for 1‑in‑3‑SAT.

Edge cases:
* No clauses → target ``0``; the empty subset always achieves it, matching the
  source problem's yes answer.
* Variables that never appear contribute ``0`` and can be ignored – they do not
  affect feasibility.

The reduction runs in time polynomial in the size of the input (O(m·C)).
"""

from __future__ import annotations

from typing import List, Dict, Any

BASE = 4  # Must be > max number of true variables per clause (3).


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 1‑in‑3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as defined by
        ``OneInThreeSat``.

    Returns
    -------
    dict
        ``{"numbers": [...], "target": t}`` suitable for ``SubsetSum``.
    """
    clauses: List[List[int]] = instance["clauses"]
    num_vars: int = instance["num_vars"]

    # Pre‑compute for each variable the sum of BASE**clause_index where the
    # variable appears.
    var_contrib: List[int] = [0] * (num_vars + 1)  # 1‑based indexing
    for idx, clause in enumerate(clauses):
        weight = BASE ** idx
        for var in clause:
            var_contrib[var] += weight

    # Build the numbers list – omit variables with zero contribution.
    numbers: List[int] = [value for value in var_contrib[1:] if value != 0]

    # Target: one in each clause digit.
    target = sum(BASE ** i for i in range(len(clauses)))

    return {"numbers": numbers, "target": target}

