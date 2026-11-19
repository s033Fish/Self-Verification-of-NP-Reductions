"""Reduction from One-In-Three SAT to Subset Sum.

The source problem (OneInThreeSat) is defined as:
    instance = {"num_vars": m, "clauses": [[a, b, c], ...]}
where each clause contains exactly three **distinct** positive integers
representing variable indices (1‑based).  A formula is satisfiable iff there
exists an assignment to the variables such that **exactly one** variable in
every clause evaluates to true.

The target problem (SubsetSum) expects instances of the form:
    {"numbers": [a1, a2, ...], "target": t}
where the numbers are non‑negative integers and we ask whether a sub‑list
adds up to *t*.

We implement a classic polynomial‑time many‑one reduction using a positional
base‑*B* encoding.  Choose a base ``B = 4`` – larger than the maximum possible
sum of digits (which is 3 because a clause contains three variables).  For each
clause we reserve a distinct digit position (i.e. a distinct power of ``B``).

For every variable *x_i* we create a number whose digit in position *j*
(``B**j``) is ``1`` iff *x_i* appears in clause *j*, otherwise ``0``.  Selecting
the numbers corresponding to the variables set to **true** yields a sum whose
digit in each clause position equals the number of true variables in that
clause.  Hence the sum equals the target (which has digit ``1`` in every clause
position) exactly when each clause has **one** true variable.

Formally:
    let C = number of clauses.
    base = 4
    target = Σ_{j=0}^{C-1} base**j   # digit 1 in every clause position
    for each variable i (1‑based):
        number_i = Σ_{j where i ∈ clause_j} base**j

If the formula has no clauses, it is trivially satisfiable; we map it to the
Subset‑Sum instance {"numbers": [], "target": 0}, which is also trivially
yes (empty sub‑list).

The construction runs in time polynomial in the size of the input (O(m·C)).
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a OneInThreeSat instance to a SubsetSum instance.

    Parameters
    ----------
    instance: dict
        {"num_vars": m, "clauses": [[a, b, c], ...]}

    Returns
    -------
    dict
        {"numbers": [...], "target": t} suitable for the SubsetSum
        solver.
    """

    m = int(instance.get("num_vars", 0))
    clauses: List[List[int]] = instance.get("clauses", [])
    C = len(clauses)

    # Edge case: no clauses – always yes.
    if C == 0:
        return {"numbers": [], "target": 0}

    base = 4  # larger than the maximum possible digit sum (3)

    # Pre‑compute powers of base for each clause index to avoid repeated pow.
    powers = [pow(base, j) for j in range(C)]

    # Build the number for each variable.
    # Variables are 1‑based up to m.
    var_values = [0] * (m + 1)  # index 0 unused
    for clause_idx, clause in enumerate(clauses):
        weight = powers[clause_idx]
        for var in clause:
            if 1 <= var <= m:
                var_values[var] += weight
            else:
                # Defensive: ignore out‑of‑range variables (should not happen).
                pass

    # Convert to list (skip index 0).
    numbers = var_values[1:]

    # Target has digit 1 in every clause position.
    target = sum(powers)

    return {"numbers": numbers, "target": target}

