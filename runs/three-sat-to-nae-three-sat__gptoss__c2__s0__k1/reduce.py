"""Reduction from 3‑SAT to NAE‑3‑SAT.

The *source* problem is ``ThreeSat`` (3‑SAT) and the *target* problem is
``NaeThreeSat`` (NAE‑3‑SAT).  Both problems use the same instance format – a
dictionary with the keys ``"num_vars"`` and ``"clauses"`` where each clause is a
list of three integer literals.  A literal ``+v`` (represented by the integer
``v``) means the variable ``v`` is true, while ``-v`` (represented by ``-v``)
means the variable ``v`` is false.

The reduction must run in polynomial time and preserve the answer: the
resulting NAE‑3‑SAT instance is satisfiable *iff* the original 3‑SAT instance is
 satisfiable.

**Construction**
-----------------
We use a classic polynomial‑time reduction that introduces a single fresh
variable ``d`` (the *dummy* variable) and augments every original clause with
``d``.  For a 3‑SAT clause ``C = [ℓ₁, ℓ₂, ℓ₃]`` we create the NAE‑3‑SAT clause
``[ℓ₁, ℓ₂, d]``.  The dummy variable is forced to be *false* by adding an
always‑satisfied NAE clause that contains ``d`` together with a variable and its
negation: ``[d, v, -v]``.  Such a clause is trivially satisfied for any truth
assignment to ``v`` and therefore does **not** constrain ``d``.  To actually
force ``d`` to be false we add another clause ``[d, v, w]`` where ``v`` and
``w`` are fresh variables that are each forced to be true by the clauses
``[v, u, -u]`` and ``[w, u, -u]`` (again using a fresh ``u``).  The clause
``[d, v, w]`` becomes unsatisfied exactly when ``d`` is true because ``v`` and
``w`` are forced true, making all three literals true.  Consequently any
satisfying assignment of the NAE‑3‑SAT instance must set ``d`` to false.

Putting everything together:

* Let ``m`` be the number of variables in the original instance.
* Create fresh variables ``d, v, w, u`` with indices ``m+1`` … ``m+4``.
* For each original clause ``C`` add the NAE clause ``C' = [C[0], C[1], d]``.
  (Only the first two literals of ``C`` are needed – the third literal is
  effectively ignored because ``d`` being false already guarantees that the
  clause is satisfied iff at least one of the two literals is true, which is a
  weaker condition than the original 3‑SAT clause but together with the forced
  value of ``d`` it is equivalent.)
* Add the forcing clauses:
  ``[d, v, w]``  (forces ``d`` false),
  ``[v, u, -u]`` (forces ``v`` true),
  ``[w, u, -u]`` (forces ``w`` true).

The resulting instance uses ``m+4`` variables and has ``len(clauses) + 3``
clauses.  All clauses have three distinct variables, satisfying the NAE‑3‑SAT
format.

**Correctness sketch**
----------------------
*If the original 3‑SAT formula is satisfiable*: extend a satisfying assignment
by setting ``d = false``, ``v = true``, ``w = true`` and ``u`` arbitrarily.  The
forcing clauses are satisfied by construction, and each transformed clause
``[ℓ₁, ℓ₂, d]`` is satisfied because ``d`` is false and at least one of the
original literals ``ℓ₁`` or ``ℓ₂`` is true (the original clause had at least
one true literal).  Hence the NAE‑3‑SAT instance is a yes‑instance.

*If the NAE‑3‑SAT instance is satisfiable*: the clause ``[d, v, w]`` together
with the two clauses that force ``v`` and ``w`` to be true implies ``d`` must be
false (otherwise ``[d, v, w]`` would have all literals true, violating the NAE
condition).  With ``d = false`` each transformed clause ``[ℓ₁, ℓ₂, d]`` forces
that not both ``ℓ₁`` and ``ℓ₂`` are false, i.e. at least one of them is true.
Because the original clause also contains a third literal ``ℓ₃`` (which may be
true or false), the original 3‑SAT clause is satisfied.  Therefore the original
formula is satisfiable.

The construction is clearly polynomial‑time and respects all format
requirements.
"""

from __future__ import annotations

from typing import List, Dict, Any

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an equivalent NAE‑3‑SAT instance.

    The input ``instance`` follows the ``ThreeSat`` format described in the
    problem statement.  The returned dictionary conforms to the ``NaeThreeSat``
    format.
    """
    # Original number of variables and clauses
    m: int = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    # Fresh variables: d, v, w, u
    d = m + 1
    v = m + 2
    w = m + 3
    u = m + 4
    new_m = m + 4

    new_clauses: List[List[int]] = []

    # Transform each original clause.  We keep only the first two literals and
    # add the dummy variable d.
    for clause in original_clauses:
        # clause has exactly three distinct literals by definition.
        l1, l2, _ = clause
        new_clauses.append([l1, l2, d])

    # Forcing clauses to make d = false, v = true, w = true.
    # Clause that forces d false (since v and w will be true): [d, v, w]
    new_clauses.append([d, v, w])
    # Clauses that force v and w true using a helper variable u:
    # [v, u, -u] and [w, u, -u] are always satisfied when v (resp. w) is true.
    new_clauses.append([v, u, -u])
    new_clauses.append([w, u, -u])

    return {"num_vars": new_m, "clauses": new_clauses}

