"""Reduction from One-In-Three SAT to Subset Sum.

The source problem (OneInThreeSat) is defined in ``problems.py`` with the
following instance format::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

All literals are positive variables (1‑based indices).  An assignment is a
selection of a subset of the variables to be *true*.  The formula is satisfied
iff **exactly one** variable in every clause is true.

The target problem (SubsetSum) expects an instance of the form::

    {"numbers": [a1, a2, ...], "target": t}

where the numbers are non‑negative integers.  The answer is *yes* iff some
sub‑list of ``numbers`` sums to ``t``.

--- Reduction idea ----------------------------------------------------------

We encode each clause as a digit in a mixed‑radix representation.  Choose a
base ``B`` larger than the maximum possible number of true literals that can
appear in a single clause.  Because each clause contains exactly three
different variables, setting ``B = 4`` is sufficient (the sum per clause will
never exceed three, so no carry can occur).

For clause ``j`` (0‑based) we associate the weight ``B**j``.  For a variable
``x_i`` we create a number that contains a ``1`` in every digit corresponding
to a clause where ``x_i`` occurs.  Concretely, the number for ``x_i`` is::

    n_i = sum_{j where i in clause_j} B**j

Selecting a subset of these numbers corresponds exactly to setting the
associated variables to true.  The sum of the selected numbers therefore has
in each digit ``j`` the count of true variables in clause ``j``.

The target we want is a number whose every digit is ``1`` – i.e. exactly one
true literal per clause.  Hence::

    target = sum_{j=0}^{c-1} B**j

where ``c`` is the number of clauses.  Because ``B`` is larger than the
maximum possible digit value, the equality of the sum in ordinary integer
addition is equivalent to the per‑digit equality required by the SAT
condition.

If the formula has no clauses, the target is ``0`` and the empty subset always
meets it, matching the source problem's definition (a formula with no clauses
is trivially satisfiable).

The construction runs in time polynomial in the size of the input (linear in
the number of variable‑clause incidences).
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a One‑In‑Three SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[a, b, c], ...]}``

    Returns
    -------
    dict
        ``{"numbers": [...], "target": t}`` suitable for the SubsetSum
        solver.
    """

    # Extract data
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Base larger than the maximum possible per‑clause count (3).  4 is safe
    # and keeps the numbers reasonably small.
    B = 4

    c = len(clauses)

    # Pre‑compute powers of B for each clause index to avoid recomputation.
    powers = [B ** j for j in range(c)]

    # Build the number for each variable (1‑based indexing).
    numbers: List[int] = [0] * m  # index i corresponds to variable i+1
    for idx, clause in enumerate(clauses):
        weight = powers[idx]
        for var in clause:
            # Variables are guaranteed to be in 1..m.
            numbers[var - 1] += weight

    # Target: one true literal per clause → digit 1 in each position.
    target = sum(powers)

    return {"numbers": numbers, "target": target}

