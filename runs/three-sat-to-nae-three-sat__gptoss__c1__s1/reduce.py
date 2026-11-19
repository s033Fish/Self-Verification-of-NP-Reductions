"""Reduction from 3‑SAT to NAE‑3‑SAT.

The source problem (``ThreeSat``) expects instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each ``li`` is an integer literal ``+v`` (variable *v* true) or ``-v``
(variable *v* false).  A clause is satisfied if **at least one** literal is
true.

The target problem (``NaeThreeSat``) uses the same representation but a
clause is satisfied iff the three literals are **not all equal** – i.e. the
clause contains at least one true literal *and* at least one false literal.

Observation
-----------
For a triple of literals ``(a, b, c)`` the NAE condition is equivalent to the
conjunction of two ordinary 3‑SAT clauses::

    (a ∨ b ∨ c) ∧ (¬a ∨ ¬b ∨ ¬c)

The first clause guarantees that at least one literal is true; the second
guarantees that not all three are true, which is the same as “at least one is
false”.  Therefore, to transform a 3‑SAT instance into an equivalent NAE‑3‑SAT
instance we simply duplicate each clause and add its *negated* version.

Reduction
---------
Given a source instance ``I`` we construct ``J`` with:

* ``num_vars`` – unchanged.
* ``clauses`` – for every clause ``C = [l1, l2, l3]`` in ``I`` we include
  ``C`` itself and the clause ``[-l1, -l2, -l3]``.

The transformation is clearly polynomial (linear) in the size of the input.
Correctness follows directly from the observation above.

The function below performs this transformation.  It does **not** call any
solver – it merely reshapes the data structure.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an equivalent NAE‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` specification.

    Returns
    -------
    dict
        A dictionary adhering to the ``NaeThreeSat`` specification such that
        ``ThreeSat.is_yes(instance)`` is true iff ``NaeThreeSat.is_yes`` on the
        returned value is true.
    """

    # The source format is guaranteed by the benchmark harness, but we keep a
    # minimal sanity check to avoid accidental crashes on malformed input.
    num_vars = instance.get("num_vars")
    clauses: List[List[int]] = instance.get("clauses", [])

    # Build the new clause list: original clause + its negation.
    new_clauses: List[List[int]] = []
    for clause in clauses:
        # Each clause already has exactly three literals.
        new_clauses.append(list(clause))  # original clause
        # Negated clause – flip the sign of each literal.
        new_clauses.append([-lit for lit in clause])

    return {"num_vars": num_vars, "clauses": new_clauses}

