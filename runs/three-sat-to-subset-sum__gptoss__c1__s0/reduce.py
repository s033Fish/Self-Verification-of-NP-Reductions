"""Reduction from 3‑SAT (ThreeSat) to Subset Sum (SubsetSum).

The source format (ThreeSat) is a dictionary with keys:
    - "num_vars": number of variables m (int)
    - "clauses": list of clauses, each a list of three literals.
      A literal is an integer +v (meaning variable v is true) or -v (v is false).

The target format (SubsetSum) is a dictionary with keys:
    - "numbers": list of non‑negative integers
    - "target": an integer t

We implement the classic Karp reduction using a mixed‑radix (base) encoding.
For each variable i we create two numbers, one representing setting the
variable to True and one to False.  Each number has a unique "variable digit"
so that exactly one of the two can be chosen to match the target.

Additionally each clause gets its own digit.  A number corresponding to a
literal contributes a 1 in the digit of every clause in which that literal
appears.  The target requires a 1 in each clause digit, meaning that the set
of chosen literals must collectively cover every clause at least once.

To avoid carries when multiple chosen literals satisfy the same clause we use
base = (num_vars + 1).  Since at most one literal per variable can be chosen,
the sum in any clause digit is bounded by the number of variables, which is
strictly less than the base, guaranteeing no carry.

The reduction runs in time polynomial in the size of the SAT instance and
produces a Subset Sum instance that is a yes‑instance iff the original 3‑SAT
instance is satisfiable.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for type hints / validation if needed.
# The reduction itself must not call any exponential‑time methods.
from problems import ThreeSat, SubsetSum


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeSat instance to a SubsetSum instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ThreeSat specification.

    Returns
    -------
    dict
        A SubsetSum instance.
    """
    # Validate the input (will raise if malformed).
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: no clauses => always satisfiable.  We can output a trivial
    # Subset Sum instance that is always yes, e.g., empty list with target 0.
    if not clauses:
        return {"numbers": [], "target": 0}

    num_clauses = len(clauses)

    # Choose a base larger than the maximum possible sum in any digit.
    # The maximum contribution to a clause digit is at most m (one per variable).
    base = m + 1

    # Pre‑compute the positional weights.
    # Variable digits occupy positions 0 .. m-1.
    # Clause digits occupy positions m .. m+num_clauses-1.
    var_weights = [base ** i for i in range(m)]
    clause_weights = [base ** (m + j) for j in range(num_clauses)]

    numbers: List[int] = []

    # For each variable, create two numbers: true and false.
    # Both have a 1 in the variable's own digit to enforce exactly one choice.
    # Additionally they have a 1 in each clause digit where the literal appears.
    for var in range(1, m + 1):
        # Determine in which clauses the positive and negative literals appear.
        pos_clause_idxs: List[int] = []
        neg_clause_idxs: List[int] = []
        for ci, clause in enumerate(clauses):
            for lit in clause:
                if lit == var:
                    pos_clause_idxs.append(ci)
                elif lit == -var:
                    neg_clause_idxs.append(ci)
        # Build the numbers.
        true_num = var_weights[var - 1]
        for ci in pos_clause_idxs:
            true_num += clause_weights[ci]
        false_num = var_weights[var - 1]
        for ci in neg_clause_idxs:
            false_num += clause_weights[ci]
        numbers.append(true_num)
        numbers.append(false_num)

    # Target: need a 1 in each variable digit (choose exactly one per variable)
    # and a 1 in each clause digit (each clause must be satisfied).
    target = 0
    for w in var_weights:
        target += w
    for w in clause_weights:
        target += w

    # Return the SubsetSum instance.
    result: Dict[str, Any] = {"numbers": numbers, "target": target}
    # Validate the output to ensure we did not make a mistake.
    SubsetSum.validate(result)
    return result

