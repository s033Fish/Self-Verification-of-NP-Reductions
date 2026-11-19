"""Reduction from 3‑SAT to Subset Sum.

The source problem is ``ThreeSat`` with instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (variable ``v`` must be true)
or ``-v`` (variable ``v`` must be false).  The target problem is ``SubsetSum``
with instances of the form::

    {"numbers": [a1, a2, ...], "target": t}

We implement the classic polynomial‑time reduction that encodes a variable
assignment as a selection of numbers.  The construction works in base 10 –
the base is larger than the maximum sum that can appear in any digit (at most
three literals per clause), so carries never occur.

Construction details
---------------------
* Let ``m`` be the number of variables and ``n`` the number of clauses.
* We view each number as a vector of ``m + n`` decimal digits.  The first ``m``
  positions correspond to variables, the last ``n`` positions correspond to
  clauses.
* For each variable ``i`` (1‑based) we create two numbers:
    - ``true_i``  – digit ``1`` in the variable position ``i`` and a ``1`` in
      each clause position where the literal ``+i`` appears.
    - ``false_i`` – digit ``1`` in the variable position ``i`` and a ``1`` in
      each clause position where the literal ``-i`` appears.
  Selecting exactly one of ``true_i`` or ``false_i`` encodes the truth value of
  variable ``i`` and contributes ``1`` to the variable digit.
* For each clause ``j`` we add a *filler* number that has a single ``1`` in the
  clause position ``j``.  These numbers allow us to force the sum of the clause
  digits to be exactly ``1``.
* The target vector has a ``1`` in every variable position (forcing exactly one
  of the two numbers per variable to be chosen) and a ``1`` in every clause
  position (forcing at least one literal in the clause to be satisfied; the
  filler numbers take care of any remaining deficit).

Because the base (10) exceeds the maximum possible digit sum (≤3), the vector
addition translates directly to integer addition without carries.  Hence a
subset of the constructed numbers sums to the target integer iff the original
3‑SAT formula is satisfiable.

The reduction runs in time polynomial in ``m`` and ``n`` and uses only basic
Python arithmetic.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _vector_to_int(vec: List[int]) -> int:
    """Convert a list of decimal digits (most‑significant first) to an int.

    ``vec`` is interpreted as a base‑10 number where ``vec[0]`` is the most
    significant digit.  Python's arbitrary‑precision integers handle the size.
    """
    # Build the integer by iterating over the digits.
    value = 0
    for d in vec:
        value = value * 10 + d
    return value


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Subset‑Sum instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of literals).

    Returns
    -------
    dict
        A Subset‑Sum instance ``{"numbers": [...], "target": t}`` that is a
        polynomial‑time transformation of the given 3‑SAT instance.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    n: int = len(clauses)

    total_digits = m + n  # length of each digit vector
    numbers: List[int] = []

    # Helper to create a vector filled with zeros.
    def zero_vec() -> List[int]:
        return [0] * total_digits

    # Build true/false numbers for each variable.
    for var in range(1, m + 1):
        # true assignment (+var)
        tv = zero_vec()
        tv[var - 1] = 1  # variable digit
        # false assignment (-var)
        fv = zero_vec()
        fv[var - 1] = 1

        for clause_idx, clause in enumerate(clauses):
            if var in clause:
                # literal +var appears
                tv[m + clause_idx] = 1
            elif -var in clause:
                # literal -var appears
                fv[m + clause_idx] = 1
            # literals are guaranteed not to contain both var and -var

        numbers.append(_vector_to_int(tv))
        numbers.append(_vector_to_int(fv))

    # Add filler numbers, one per clause.
    for clause_idx in range(n):
        filler = zero_vec()
        filler[m + clause_idx] = 1
        numbers.append(_vector_to_int(filler))

    # Construct the target vector: 1 in every variable and clause position.
    target_vec = [1] * total_digits
    target = _vector_to_int(target_vec)

    return {"numbers": numbers, "target": target}

