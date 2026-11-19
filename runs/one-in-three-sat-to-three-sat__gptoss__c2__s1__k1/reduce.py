"""Reduction from One-In-Three SAT to 3-SAT.

The source problem (``OneInThreeSat``) expects instances of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where each clause contains three *positive* distinct variable indices.
An assignment satisfies the instance iff **exactly one** variable in each
clause is set to ``True``.

The target problem (``ThreeSat``) expects a classic 3‑CNF instance where
each clause is a list of three *literals* ``l``.  A literal is an integer:
positive ``v`` denotes the variable ``v`` being ``True`` and negative ``-v``
denotes the variable ``v`` being ``False``.  Clauses must contain three
different variables and may not contain both a variable and its negation.

The reduction is straightforward: for each original clause ``(a, b, c)`` we
need to enforce two conditions:

1. **At least one** of ``a, b, c`` is true – this is already a 3‑literal
   clause ``[a, b, c]``.
2. **At most one** of ``a, b, c`` is true – for every pair we add the
   constraint ``¬a ∨ ¬b``.  A 2‑literal clause can be simulated with two
   3‑literal clauses using a fresh auxiliary variable ``t``:

       (¬a ∨ ¬b)   ⇔   (¬a ∨ ¬b ∨  t) ∧ (¬a ∨ ¬b ∨ ¬t)

   The equivalence holds because if ``¬a ∨ ¬b`` is satisfied, both new
   clauses are satisfied regardless of ``t``; otherwise ``a = b = True``
   forces the two clauses to require ``t`` and ``¬t`` simultaneously – an
   impossibility.

For each original clause we therefore create one 3‑positive clause and six
clauses of the form described above (two per pair).  All auxiliary variables
are fresh and distinct, guaranteeing that each clause contains three
different variables as required by the ``ThreeSat`` format.

The construction runs in linear time in the size of the input and clearly
preserves satisfiability: a satisfying assignment for the original instance
can be extended arbitrarily to the auxiliary variables, and any satisfying
assignment of the produced 3‑SAT instance restricts to a satisfying assignment
of the original one because the auxiliary clauses enforce the “exactly one”
condition.

The ``reduce`` function implements this transformation.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a One‑In‑Three SAT instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of positive integers).

    Returns
    -------
    dict
        A 3‑SAT instance in the format required by ``ThreeSat``.
    """

    m: int = instance.get("num_vars", 0)
    original_clauses: List[List[int]] = instance.get("clauses", [])

    # If there are no clauses, the instance is trivially satisfiable for any
    # number of variables.  The target format also allows an empty clause list,
    # so we simply return a 3‑SAT instance with the same number of variables.
    if not original_clauses:
        return {"num_vars": m, "clauses": []}

    new_clauses: List[List[int]] = []
    # Fresh auxiliary variables start after the original ones.
    next_fresh: int = m + 1

    for clause in original_clauses:
        if len(clause) != 3:
            # Defensive programming – the source validator guarantees this,
            # but we keep the check to avoid malformed input causing obscure
            # errors later.
            raise ValueError("Each OneInThreeSat clause must contain exactly three literals")

        a, b, c = clause
        # 1. At least one true.
        new_clauses.append([a, b, c])

        # 2. At most one true – enforce ¬a ∨ ¬b, ¬a ∨ ¬c, ¬b ∨ ¬c.
        pairs = [(a, b), (a, c), (b, c)]
        for x, y in pairs:
            t = next_fresh
            next_fresh += 1
            # (¬x ∨ ¬y ∨  t) and (¬x ∨ ¬y ∨ ¬t)
            new_clauses.append([-x, -y, t])
            new_clauses.append([-x, -y, -t])

    new_num_vars = next_fresh - 1
    return {"num_vars": new_num_vars, "clauses": new_clauses}

