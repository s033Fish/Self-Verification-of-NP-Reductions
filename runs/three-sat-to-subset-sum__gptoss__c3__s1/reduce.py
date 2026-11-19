"""Reduction from 3-SAT to Subset Sum.

The source problem is :class:`problems.ThreeSat` and the target is
``problems.SubsetSum``.  Both classes are defined in ``problems.py`` and
provide static methods ``validate`` and ``is_yes``.

We implement the classic polynomial‑time reduction using a positional
encoding (base‑B representation).  For a formula with ``m`` variables and
``k`` clauses we construct ``2*m`` numbers – one representing the literal
``x_i`` being true and one representing ``¬x_i`` being false.  Each number
has ``m + k`` digit positions (least‑significant digit corresponds to the
first variable).  The first ``m`` positions enforce that exactly one of the
two numbers for each variable is chosen (they each contribute a ``1`` in the
variable's position).  The remaining ``k`` positions correspond to clauses;
whenever a literal appears in a clause we place a ``1`` in that clause's
position.  The target vector has a ``1`` in every variable position (so we
must pick exactly one literal per variable) and a ``1`` in every clause
position (so each clause must be satisfied by at least one chosen literal).

Choosing a base ``B`` larger than the maximum possible sum in any digit
position prevents carries.  Each digit can receive at most three contributions
from literals of a clause, so ``B = 4`` would suffice; we use ``B = 10`` for
clarity.

The reduction runs in time polynomial in ``m`` and ``k`` and returns a
valid Subset Sum instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, SubsetSum


def _vec_to_int(vec: List[int], base: int) -> int:
    """Convert a list of digits (least‑significant first) to an integer.

    ``vec[i]`` is the digit for position ``i``.  ``base`` must be larger than
    any possible digit sum to avoid carries.
    """
    value = 0
    multiplier = 1
    for digit in vec:
        value += digit * multiplier
        multiplier *= base
    return value


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Subset Sum instance.

    The returned dictionary follows the format required by
    ``SubsetSum.validate``: ``{"numbers": [...], "target": t}``.
    """
    # Validate the source instance – this will raise if malformed.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    k: int = len(clauses)

    # Edge case: no variables and no clauses -> trivially satisfiable.
    if m == 0 and k == 0:
        return {"numbers": [], "target": 0}

    base = 10  # larger than max digit sum (≤3) to avoid carries.
    length = m + k  # total number of digit positions.

    numbers: List[int] = []

    # Pre‑compute which clauses each literal appears in.
    # clause_of_literal[literal] = list of clause indices where it occurs.
    clause_of_literal: Dict[int, List[int]] = {}
    for idx, clause in enumerate(clauses):
        for lit in clause:
            clause_of_literal.setdefault(lit, []).append(idx)

    for var in range(1, m + 1):
        # True literal (+var)
        vec_true = [0] * length
        vec_true[var - 1] = 1  # variable position
        for cid in clause_of_literal.get(var, []):
            vec_true[m + cid] = 1
        numbers.append(_vec_to_int(vec_true, base))

        # False literal (-var)
        vec_false = [0] * length
        vec_false[var - 1] = 1
        for cid in clause_of_literal.get(-var, []):
            vec_false[m + cid] = 1
        numbers.append(_vec_to_int(vec_false, base))

    # Build target vector: 1 for each variable and 1 for each clause.
    target_vec = [1] * length
    target = _vec_to_int(target_vec, base)

    # Construct the Subset Sum instance.
    subset_instance: Dict[str, Any] = {"numbers": numbers, "target": target}
    # Validate the target instance (optional but ensures correctness).
    SubsetSum.validate(subset_instance)
    return subset_instance

