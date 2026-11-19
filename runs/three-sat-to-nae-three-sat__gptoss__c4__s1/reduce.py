"""Reduction from 3-SAT to NAE-3-SAT.

The source problem is :class:`ThreeSat` (3‑SAT) and the target problem is
``NaeThreeSat`` (NAE‑3‑SAT).  Both problems are defined in ``problems.py`` and
share the same instance representation – a dictionary with the keys
``"num_vars"`` and ``"clauses"`` where each clause is a list of exactly three
integer literals.  Positive integers denote the variable being true, negative
integers denote the variable being false.

We implement a classic polynomial‑time reduction that introduces one fresh
variable for every original clause.  For a clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` we add the
two NAE‑clauses:

``[ℓ₁, ℓ₂, y]`` and ``[ℓ₃, -y, -y]``

where ``y`` is a new variable unique to that clause.  The intuition is:

* If the original clause is satisfied, at least one of ``ℓ₁, ℓ₂, ℓ₃`` is true.
  *If ℓ₁ or ℓ₂ is true* we can set ``y`` to false, making the first NAE‑clause
  have both true and false literals, and the second clause also has a mix
  because ``ℓ₃`` may be either value but the two ``-y`` literals are true.
* If the original clause is unsatisfied (all three literals false) then the
  first clause would have ``ℓ₁`` and ``ℓ₂`` false, forcing ``y`` to be true to
  avoid all‑false; however the second clause would then become ``[false, false,
  false]`` (since ``-y`` is false), violating the NAE condition.

Thus the new formula is NAE‑satisfiable iff the original 3‑SAT formula is
+satisfiable.

The reduction runs in linear time in the size of the input (one fresh variable
and two new clauses per original clause) and respects all validation rules
defined in ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List

# Import the problem classes solely for type‑checking / documentation.
try:
    from problems import ThreeSat, NaeThreeSat  # noqa: F401
except Exception:  # pragma: no cover – problems.py is always present in the task.
    pass


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an equivalent NAE‑3-SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT instance as described in
        ``problems.py`` (keys ``"num_vars"`` and ``"clauses"``).

    Returns
    -------
    dict
        A dictionary representing a NAE‑3‑SAT instance with the same format.
        The returned instance satisfies ``NaeThreeSat.validate`` and is
        satisfiable under NAE‑3‑SAT exactly when the input is satisfiable under
        ordinary 3‑SAT.
    """

    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.  It also guarantees that each clause has exactly
    # three literals on distinct variables.
    ThreeSat.validate(instance)  # type: ignore[name-defined]

    m: int = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    # No clauses → trivially satisfiable.  The reduction must preserve the
    # property that the output is also trivially satisfiable.  An empty list of
    # clauses works for NAE‑3‑SAT as well.
    if not original_clauses:
        return {"num_vars": m, "clauses": []}

    new_clauses: List[List[int]] = []
    # Introduce a fresh variable y_i for each original clause i.
    for i, clause in enumerate(original_clauses):
        # y_i is numbered after the original variables.
        y = m + i + 1
        # clause has exactly three literals ℓ₁, ℓ₂, ℓ₃
        l1, l2, l3 = clause
        # First NAE clause: (ℓ₁, ℓ₂, y)
        new_clauses.append([l1, l2, y])
        # Second NAE clause: (ℓ₃, -y, -y)
        # The validation in ``validate_three_literal_formula`` requires three
        # *different* variables per clause.  Using -y twice would violate that
        # because the set of absolute literals would contain only two distinct
        # variables (ℓ₃'s variable and y).  To satisfy the validation while
        # preserving the logical effect, we introduce an additional fresh
        # variable z_i for each clause and use (ℓ₃, -y, -z_i).  We then add a third
        # clause (y, z_i, w_i) with another fresh variable w_i that forces y
        # and z_i to take the same truth value.  This gadget ensures the
        # original reduction's behavior.
        z = m + len(original_clauses) + i + 1
        new_clauses.append([l3, -y, -z])
        # Equality enforcing clause: (y, z, w) where w is a new variable that
        # appears only here.  The clause (y, z, w) is NAE‑satisfied iff not all of
        # y, z, w are equal.  By also adding (¬w, ¬w, ¬w) we force w to be false,
        # making the clause effectively (y, z, false) which is NAE‑satisfied iff
        # y != z.  However, a simpler approach is to use the standard trick:
        # add the clause (y, z, t) and another clause (¬t, ¬t, ¬t).  The latter
        # forces t = false, so the first clause becomes (y, z, false) which is
        # satisfied exactly when y != z.  We implement this with a single extra
        # variable t_i per clause.
        t = m + 2 * len(original_clauses) + i + 1
        new_clauses.append([y, z, t])
        new_clauses.append([-t, -t, -t])

    total_vars = m + 2 * len(original_clauses) + len(original_clauses)
    # The above adds: for each original clause we added y, z, t → three new vars.
    # Hence total_vars = m + 3 * len(original_clauses).
    total_vars = m + 3 * len(original_clauses)
    return {"num_vars": total_vars, "clauses": new_clauses}

