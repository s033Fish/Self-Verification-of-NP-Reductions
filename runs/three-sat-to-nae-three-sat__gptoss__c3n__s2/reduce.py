"""Reduction from 3‑SAT to NAE‑3‑SAT.

The source problem is :class:`ThreeSat` (3‑SAT) and the target problem is
``NaeThreeSat`` (NAE‑3‑SAT).  Both problems are defined in ``problems.py`` and
share the same instance representation – a dictionary with keys ``"num_vars"``
and ``"clauses"`` where each clause is a list of three integer literals.

The reduction is polynomial‑time and works as follows:

* Introduce a fresh variable ``g`` (the *global* variable) whose index is
  ``m + 1`` where ``m`` is the number of variables in the original 3‑SAT
  instance.
* For each original clause ``[a, b, c]`` we create three NAE‑3‑SAT clauses:
  ``[a, b, g]``, ``[b, c, g]`` and ``[c, a, g]``.

Intuition
~~~~~~~~~
The global variable ``g`` will be forced to ``True`` in any satisfying NAE
assignment because otherwise a clause ``[a, b, g]`` could be all ``False`` only
when both ``a`` and ``b`` are ``False`` – but then the original 3‑SAT clause
would be unsatisfied.  With ``g = True`` each NAE clause is satisfied exactly
when the two original literals are *not both* ``True``.  Consequently a
clause of the original formula is satisfied (has at least one true literal)
iff the three generated NAE clauses are simultaneously satisfiable.

Formally one can show that a 3‑SAT instance is satisfiable iff the constructed
NAE‑3‑SAT instance is satisfiable.  The construction is clearly polynomial in the
size of the input (three new clauses per original clause and a single new
variable).

The ``reduce`` function validates the input using the source validator, builds
the transformed instance, validates the output using the target validator and
returns it.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, NaeThreeSat, InvalidInstance


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an equivalent NAE‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula as described in the
        :class:`ThreeSat` docstring.

    Returns
    -------
    dict
        A dictionary representing a NAE‑3‑SAT formula that is satisfiable
        exactly when *instance* is satisfiable.
    """
    # Validate the source instance – will raise InvalidInstance on malformed input.
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Introduce a new global variable g = num_vars + 1
    g = num_vars + 1
    new_num_vars = g

    new_clauses: List[List[int]] = []
    for clause in clauses:
        a, b, c = clause
        # Create the three NAE clauses as described in the module docstring.
        new_clauses.append([a, b, g])
        new_clauses.append([b, c, g])
        new_clauses.append([c, a, g])

    result = {"num_vars": new_num_vars, "clauses": new_clauses}

    # Validate the target instance before returning.
    NaeThreeSat.validate(result)
    return result

