"""Reduction from 3‑SAT to NAE‑3‑SAT.

The source problem is :class:`ThreeSat` (3‑SAT) and the target problem is
``NaeThreeSat`` (NAE‑3‑SAT).  Both problems are defined in ``problems.py`` and
share the same instance format – a dictionary with ``"num_vars"`` and a list of
clauses, each clause being a list of three integer literals.

The reduction is a classic polynomial‑time transformation that introduces one
fresh auxiliary variable per clause.  For an original clause ``(ℓ1, ℓ2, ℓ3)``
we create two NAE‑3‑SAT clauses:

``[ℓ1, ℓ2,  a]`` and ``[ℓ2, ℓ3, -a]``

where ``a`` is a new variable (different for each original clause).  The
intuition is:

* If all three original literals are false, the first new clause forces ``a``
  to be true, while the second clause then becomes ``[false, false, false]`` –
  which violates the NAE condition.  Hence the original clause cannot be all
  false.
* If at least one original literal is true, we can choose a suitable truth
  value for ``a`` (either true or false) so that both NAE clauses are satisfied.

This construction preserves satisfiability: the original 3‑SAT formula is
 satisfiable iff the resulting NAE‑3‑SAT formula is.

The implementation below performs the transformation, validates the input
using the ``ThreeSat.validate`` method, and returns a correctly formatted
NAE‑3‑SAT instance.
"""

from __future__ import annotations

from typing import List, Dict

from problems import ThreeSat, NaeThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an equivalent NAE‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula as described in the
        ``ThreeSat`` docstring.

    Returns
    -------
    dict
        A dictionary representing a NAE‑3‑SAT formula.  The number of variables
        is the original ``num_vars`` plus one fresh variable for each clause.
    """
    # Validate the source instance – this will raise InvalidInstance on bad input.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    # Each original clause gets a fresh auxiliary variable.
    k = len(original_clauses)
    new_num_vars = m + k

    new_clauses: List[List[int]] = []
    # auxiliary variable indices start at m+1 and increase.
    for idx, clause in enumerate(original_clauses, start=1):
        # clause has exactly three literals ℓ1, ℓ2, ℓ3
        l1, l2, l3 = clause
        aux = m + idx  # positive literal for the auxiliary variable
        # First NAE clause: (ℓ1, ℓ2,  a)
        new_clauses.append([l1, l2, aux])
        # Second NAE clause: (ℓ2, ℓ3, -a)
        new_clauses.append([l2, l3, -aux])

    reduced_instance = {"num_vars": new_num_vars, "clauses": new_clauses}
    # Validate the produced instance just to be safe.
    NaeThreeSat.validate(reduced_instance)
    return reduced_instance

